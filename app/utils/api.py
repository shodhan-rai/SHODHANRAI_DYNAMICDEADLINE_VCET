import requests
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from config.config import ASANA_API_URL, HEADERS

def update_due_date(task_id, priority):
    """Update the due date of a task based on its priority."""
    due_date = calculate_due_date(priority)
    url = f"{ASANA_API_URL}/tasks/{task_id}"
    payload = {"data": {"due_on": due_date}}
    
    response = requests.put(url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        print(f"Task {task_id} due date set to {due_date} based on {priority} priority")
    else:
        raise Exception(f"Failed to update due date: {response.status_code}")

def calculate_due_date(priority):
    """Calculate due date based on priority level."""
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

def extend_due_dates_in_progress(section_id, excluded_task_id=None):
    """Extend due dates for all tasks in the given section except the excluded task."""
    url = f"{ASANA_API_URL}/sections/{section_id}/tasks"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        tasks = response.json()['data']
        print(f"Extending due dates for {len(tasks)-1} tasks in 'In Progress' section")
        
        for task in tasks:
            task_id = task['gid']
            if task_id == excluded_task_id:
                continue
            extend_due_date(task_id, 2)
    else:
        raise Exception(f"Failed to fetch tasks: {response.status_code}")

def extend_due_date(task_id, days):
    """Extend the due date of a specific task by the given number of days."""
    url = f"{ASANA_API_URL}/tasks/{task_id}"
    
    # Get current task details
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return
    
    task = response.json()['data']
    current_due_date = task.get('due_on')
    
    if not current_due_date:
        return
    
    # Calculate and set new due date
    due_date = datetime.strptime(current_due_date, "%Y-%m-%d") + timedelta(days=days)
    payload = {"data": {"due_on": due_date.strftime("%Y-%m-%d")}}
    
    response = requests.put(url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        print(f"Extended due date for task {task_id} by {days} days to {due_date.strftime('%Y-%m-%d')}")
    else:
        raise Exception(f"Failed to extend due date: {response.status_code}")

def get_task_details(task_id):
    """Get detailed information about a specific task."""
    url = f"{ASANA_API_URL}/tasks/{task_id}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json()['data']
    return {}

def get_tasks_in_section(section_id):
    """Get all tasks in a specific section."""
    url = f"{ASANA_API_URL}/sections/{section_id}/tasks"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json()['data']
    return []