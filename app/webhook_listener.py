from flask import Flask, request, jsonify, make_response
from utils.api import update_due_date, extend_due_dates_in_progress, get_task_details, get_tasks_in_section
import json
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

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # Handle handshake request
    if 'X-Hook-Secret' in request.headers:
        handshake_secret = request.headers['X-Hook-Secret']
        response = make_response("", 200)
        response.headers["X-Hook-Secret"] = handshake_secret
        response.headers["Content-Type"] = "text/plain"
        return response

    # Parse JSON payload
    try:
        data = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": "Failed to decode JSON object"}), 400

    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400

    # Handle task updates or other events
    if 'events' in data:
        for event in data['events']:
            action = event.get('action')
            task = event.get('resource', {})
            task_id = task.get('gid')
            parent = event.get('parent') or {}
            section_id = parent.get('gid')

            # Handle task movement to "In Progress" section
            if action == 'added' and task.get('resource_type') == 'task' and parent.get('resource_type') == 'section':
                if section_id == IN_PROGRESS_SECTION_ID:
                    # Fetch task details to get the priority
                    task_details = get_task_details(task_id)
                    
                    if 'custom_fields' in task_details:
                        for field in task_details['custom_fields']:
                            if field.get('enum_value') and field['enum_value'].get('gid') in PRIORITY_MAPPING:
                                priority_name = PRIORITY_MAPPING[field['enum_value']['gid']]
                                if priority_name == "High":
                                    print(f"High-priority task {task_id} moved to 'In Progress' section")
                                    try:
                                        extend_due_dates_in_progress(IN_PROGRESS_SECTION_ID, task_id)
                                    except Exception as e:
                                        print(f"Error extending due dates: {str(e)}")

            # Handle due date assignment for new tasks
            if action == 'added' and task.get('resource_type') == 'task':
                task_details = get_task_details(task_id)
                initial_due_date = task_details.get('due_on')
                
                if task_details.get('name') and not initial_due_date:
                    # Check custom fields for priority
                    if 'custom_fields' in task_details:
                        for field in task_details['custom_fields']:
                            if field.get('enum_value') and field['enum_value'].get('gid') in PRIORITY_MAPPING:
                                priority = PRIORITY_MAPPING[field['enum_value']['gid']]
                                print(f"Setting initial due date for new task {task_id} with priority: {priority}")
                                update_due_date(task_id, priority)
                                break

            # Handle custom fields changes for priority updates
            elif action == 'changed' and task.get('resource_type') == 'task':
                change_field = event.get('change', {}).get('field')
                if change_field == 'custom_fields':
                    new_value = event.get('change', {}).get('new_value', {})
                    if new_value.get('resource_type') == 'custom_field' and new_value.get('enum_value'):
                        enum_value_id = new_value['enum_value']['gid']
                        if enum_value_id in PRIORITY_MAPPING:
                            priority = PRIORITY_MAPPING[enum_value_id]
                            task_details = get_task_details(task_id)
                            initial_due_date = task_details.get('due_on')
                            if not initial_due_date:
                                print(f"Setting due date for task {task_id} after priority change to: {priority}")
                                update_due_date(task_id, priority)

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)