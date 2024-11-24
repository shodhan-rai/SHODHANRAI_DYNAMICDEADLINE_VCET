from flask import Flask, request, jsonify, make_response
from utils.api import update_due_date, extend_due_dates_in_progress, get_task_details, reduce_due_dates_in_progress
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Mapping of custom field enum value IDs to priority levels
PRIORITY_MAPPING = {
    "1208780230046416": "Low",    
    "1208780230046417": "Medium",
    "1208780230046418": "High"   
}

IN_PROGRESS_SECTION_ID = os.getenv('IN_PROGRESS_SECTION_ID')

# Tracking which high priority tasks have extended which tasks
# Format: {task_id: {'extended_by': set(high_priority_task_ids)}}
task_extension_tracking = {}

# Track tasks with automatically set due dates
auto_due_date_tasks = set()

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # Handle handshake request
    if 'X-Hook-Secret' in request.headers:
        handshake_secret = request.headers['X-Hook-Secret']
        response = make_response("", 200)
        response.headers["X-Hook-Secret"] = handshake_secret
        response.headers["Content-Type"] = "text/plain"
        return response

    try:
        data = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": "Failed to decode JSON object"}), 400

    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400

    if 'events' in data:
        for event in data['events']:
            action = event.get('action')
            task = event.get('resource', {})
            task_id = task.get('gid')
            parent = event.get('parent') or {}
            section_id = parent.get('gid')

            # Handle task movement to "In Progress" section
            if (action == 'added' and 
                task.get('resource_type') == 'task' and 
                parent.get('resource_type') == 'section' and
                section_id == IN_PROGRESS_SECTION_ID):
                
                task_details = get_task_details(task_id)
                
                if 'custom_fields' in task_details:
                    for field in task_details['custom_fields']:
                        if field.get('enum_value') and field['enum_value'].get('gid') in PRIORITY_MAPPING:
                            priority_name = PRIORITY_MAPPING[field['enum_value']['gid']]
                            if priority_name == "High":
                                print(f"High-priority task {task_id} moved to 'In Progress' section")
                                try:
                                    extend_due_dates_in_progress(
                                        IN_PROGRESS_SECTION_ID, 
                                        task_id,
                                        task_extension_tracking
                                    )
                                except Exception as e:
                                    print(f"Error extending due dates: {str(e)}")

            # Handle task movement out of "In Progress" section
            elif (action == 'removed' and 
                  task.get('resource_type') == 'task' and 
                  parent.get('resource_type') == 'section' and
                  section_id == IN_PROGRESS_SECTION_ID):
                
                task_details = get_task_details(task_id)
                if 'custom_fields' in task_details:
                    for field in task_details['custom_fields']:
                        if field.get('enum_value') and field['enum_value'].get('gid') in PRIORITY_MAPPING:
                            priority_name = PRIORITY_MAPPING[field['enum_value']['gid']]
                            if priority_name == "High":
                                print(f"High-priority task {task_id} moved out of 'In Progress' section")
                                try:
                                    # Only reduce due dates for tasks that were extended by this specific task
                                    reduce_due_dates_in_progress(
                                        IN_PROGRESS_SECTION_ID,
                                        task_id,
                                        task_extension_tracking
                                    )
                                except Exception as e:
                                    print(f"Error reducing due dates: {str(e)}")

            # Handle priority changes
            if action == 'changed' and task.get('resource_type') == 'task':
                change_field = event.get('change', {}).get('field')
                if change_field == 'custom_fields':
                    new_value = event.get('change', {}).get('new_value', {})
                    if new_value.get('resource_type') == 'custom_field' and new_value.get('enum_value'):
                        enum_value_id = new_value['enum_value']['gid']
                        if enum_value_id in PRIORITY_MAPPING:
                            priority = PRIORITY_MAPPING[enum_value_id]
                            task_details = get_task_details(task_id)
                            due_date = task_details.get('due_on')
                            
                            if not due_date or task_id in auto_due_date_tasks:
                                print(f"Setting due date for task {task_id} after priority change to: {priority}")
                                update_due_date(task_id, priority)
                                auto_due_date_tasks.add(task_id)
                            else:
                                print(f"Keeping existing due date {due_date} for task {task_id} despite priority change to {priority}")

            # Handle new task creation
            elif action == 'added' and task.get('resource_type') == 'task':
                task_details = get_task_details(task_id)
                initial_due_date = task_details.get('due_on')
                
                if task_details.get('name') and not initial_due_date:
                    if 'custom_fields' in task_details:
                        for field in task_details['custom_fields']:
                            if field.get('enum_value') and field['enum_value'].get('gid') in PRIORITY_MAPPING:
                                priority = PRIORITY_MAPPING[field['enum_value']['gid']]
                                print(f"Setting initial due date for new task {task_id} with priority: {priority}")
                                update_due_date(task_id, priority)
                                auto_due_date_tasks.add(task_id)
                                break
                elif initial_due_date:
                    print(f"Keeping manually set due date {initial_due_date} for new task {task_id}")

    
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)