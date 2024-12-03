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
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
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
def extend_due_dates_in_progress(section_id, high_priority_task_id, task_extension_tracking):
    """Extend due dates for ALL tasks in the section when a high priority task enters."""
    url = f"{ASANA_API_URL}/sections/{section_id}/tasks"
    extended_tasks = set()
    
    try:
        response = api_request('get', url)
        tasks = response.json()['data']
        
        for task in tasks:
            task_id = task['gid']
            
            if task_id == high_priority_task_id:
                continue
            
            if task_id not in task_extension_tracking:
                task_extension_tracking[task_id] = {'extended_by': set()}
            
            extend_due_date(task_id, 2)
            task_extension_tracking[task_id]['extended_by'].add(high_priority_task_id)
            extended_tasks.add(task_id)
            logger.info(f"Task {task_id} extended by high priority task {high_priority_task_id}")
            
        return extended_tasks
            
    except Exception as e:
        logger.error(f"Failed to extend due dates: {str(e)}")
        raise

@handle_rate_limit
def reduce_due_dates_in_progress(section_id, high_priority_task_id, task_extension_tracking):
    """Reduce due dates for all tasks that were extended by this specific high priority task."""
    try:
        for task_id, tracking_info in list(task_extension_tracking.items()):
            if high_priority_task_id in tracking_info['extended_by']:
                task_details = get_task_details(task_id)
                if task_details.get('memberships'):
                    for membership in task_details['memberships']:
                        if membership.get('section') and membership['section']['gid'] == section_id:
                            reduce_due_date(task_id, 2)
                            tracking_info['extended_by'].remove(high_priority_task_id)
                            if not tracking_info['extended_by']:
                                del task_extension_tracking[task_id]
                            logger.info(f"Reduced due date for task {task_id} after high priority task {high_priority_task_id} moved")
                            break
                            
    except Exception as e:
        logger.error(f"Failed to reduce due dates: {str(e)}")
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
    """Calculate due date based on priority level"""
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
def reduce_due_date(task_id, days):
    """Reduce the due date of a specific task by the given number of days."""
    url = f"{ASANA_API_URL}/tasks/{task_id}"
   
    try:
        # Get current task details
        response = api_request('get', url)
        task = response.json()['data']
        current_due_date = task.get('due_on')
   
        if not current_due_date:
            return
   
        # Calculate and set new due date
        due_date = datetime.strptime(current_due_date, "%Y-%m-%d") - timedelta(days=days)
        payload = {"data": {"due_on": due_date.strftime("%Y-%m-%d")}}
   
        response = api_request('put', url, json=payload)
        logger.info(f"Reduced due date for task {task_id} by {days} days to {due_date.strftime('%Y-%m-%d')}")
        
    except Exception as e:
        logger.error(f"Failed to reduce due date for task {task_id}: {str(e)}")
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