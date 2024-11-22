import requests
import sys
import os
import time
from datetime import datetime, timedelta
from functools import wraps
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from config.config import ASANA_API_URL, HEADERS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure session with retry strategy
def create_session():
    """Create a requests session with retry strategy"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # number of retries
        backoff_factor=1,  
        status_forcelist=[429, 500, 502, 503, 504]  # status codes to retry on
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

session = create_session()

def handle_rate_limit(func):
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                response = getattr(e, 'response', None)
                if response and response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limit hit. Waiting {retry_after} seconds before retry.")
                    time.sleep(retry_after)
                    retry_count += 1
                else:
                    logger.error(f"Request failed: {str(e)}")
                    raise
        raise Exception("Max retries exceeded for rate limit")
    return wrapper

def api_request(method, url, **kwargs):
    """Function to make API requests"""
    try:
        response = session.request(method, url, headers=HEADERS, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        raise

@handle_rate_limit
def update_due_date(task_id, priority):
    """Update the due date of a task based on its priority."""
    due_date = calculate_due_date(priority)
    url = f"{ASANA_API_URL}/tasks/{task_id}"
    payload = {"data": {"due_on": due_date}}
   
    response = api_request('put', url, json=payload)
    logger.info(f"Task {task_id} due date set to {due_date} based on {priority} priority")
    return response.json()

def calculate_due_date(priority):
    """Function to Calculate due date based on priority level"""
    today = datetime.today()
    if priority == "Low":
        due_date = today + timedelta(days=14)
    elif priority == "Mid" or priority == "Medium":
        due_date = today + timedelta(days=7)
    elif priority == "High":
        due_date = today + timedelta(days=2)
    else:
        due_date = today + timedelta(days=7)  # Default case
   
    return due_date.strftime("%Y-%m-%d")

@handle_rate_limit
def extend_due_dates_in_progress(section_id, excluded_task_id=None, extended_tasks_set=None):
    """Extend due dates for all tasks in the given section except the excluded task."""
    url = f"{ASANA_API_URL}/sections/{section_id}/tasks"
    
    try:
        response = api_request('get', url)
        tasks = response.json()['data']
        logger.info(f"Extending due dates for tasks in 'In Progress' section")
        
        # Batch process tasks
        for task in tasks:
            task_id = task['gid']
            
            # Skip the task that triggered the extension and already extended tasks
            if task_id == excluded_task_id or (extended_tasks_set is not None and task_id in extended_tasks_set):
                continue
            
            # Extend due date and mark as extended
            extend_due_date(task_id, 2)
            if extended_tasks_set is not None:
                extended_tasks_set.add(task_id)
                
    except Exception as e:
        logger.error(f"Failed to extend due dates: {str(e)}")
        raise

@handle_rate_limit
def extend_due_date(task_id, days):
    """Extend the due date of a specific task by the given number of days."""
    url = f"{ASANA_API_URL}/tasks/{task_id}"
   
    try:
        # Get current task details
        response = api_request('get', url)
        task = response.json()['data']
        current_due_date = task.get('due_on')
   
        if not current_due_date:
            return
   
        # Calculate and set new due date
        due_date = datetime.strptime(current_due_date, "%Y-%m-%d") + timedelta(days=days)
        payload = {"data": {"due_on": due_date.strftime("%Y-%m-%d")}}
   
        response = api_request('put', url, json=payload)
        logger.info(f"Extended due date for task {task_id} by {days} days to {due_date.strftime('%Y-%m-%d')}")
        
    except Exception as e:
        logger.error(f"Failed to extend due date for task {task_id}: {str(e)}")
        raise

@handle_rate_limit
def get_task_details(task_id):
    """Get detailed information about a specific task."""
    url = f"{ASANA_API_URL}/tasks/{task_id}"
    try:
        response = api_request('get', url)
        return response.json()['data']
    except Exception:
        logger.error(f"Failed to get task details for task {task_id}")
        return {}

@handle_rate_limit
def get_tasks_in_section(section_id):
    """Get all tasks in a specific section."""
    url = f"{ASANA_API_URL}/sections/{section_id}/tasks"
    try:
        response = api_request('get', url)
        return response.json()['data']
    except Exception:
        logger.error(f"Failed to get tasks in section {section_id}")
        return []