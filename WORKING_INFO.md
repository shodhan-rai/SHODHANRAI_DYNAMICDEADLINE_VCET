## Working Info

### 1. Problem Understanding
   - Assign due dates automatically based on priority.
   - Extend due dates of tasks in the In Progress section when a High-priority task is added.
   - Ensure due dates are extended only once for each event.


### 2. Logic
  - Due Date Assignment:
    - High priority: Present date + 2 days.
    - Medium priority: Present date + 7 days.
    - Low priority: Present date + 14 days.
  - Due Date Extension:
    - When a High-priority task is moved to In Progress, extend the due dates of other tasks in In Progress by 2 days.

### 3. Tools and Platform
  - Used Asana API to integrate local logic with Asana platform.
  - Utilized Flask framework to set up a webhook listener for monitoring task updates.

### 4. Implementation
- Webhook Setup:
  - Created a webhook to monitor changes in Asana
  - Configured the webhook to send updates to the Flask server
- API Calls:
  - Implemented a Python module (api.py) to handle:
    - Updating task due dates.
- Logic Execution:
- Processed webhook updates in webhook_listener.py to:
  - Identify if the change affects priority or task section.
  - Trigger the logic to assign or extend due dates.


### 5. Trial and Error
Here are some challenges faced during implementation and how they were resolved:
1. **Webhook Setup:**
   - Faced difficulty understanding how to create and validate webhooks in Asana.
   - Referred to Asana documentation and examples.
  
2. **API Authentication:**
   - Errors while authenticating with the Asana API due to token mismanagement.
   - Used python-dotenv to manage tokens.

3. **Duplicate Updates:**
   - Webhook updates were causing redundant due date extensions.
   - Solved this issue by keeping track of the tasks whose due date was extended.

### 6. Code Structure

The project includes the following files:
- `webhook_listener.py`:
  - A Flask server to receive and process webhook updates from Asana. 
- `api.py`:
  - Handles API interactions, including fetching and updating tasks.
- `create_webhook.py`:
  - Creation of the webhook for monitoring changes in Asana.
