# Dynamic Deadline Automation with Asana


This project automates the assignment of due dates to tasks based on priority and extends due dates for tasks in the "In Progress" section when a high-priority task is moved to that section.

## Features
- Assigns initial due dates based on task priority:
  - Low: 14 days from the present date.
  - Mid: 7 days from the present date.
  - High: 2 days from the present date.
- Automatically extends due dates for all tasks in the "In Progress" section by 2 days when a high-priority task is moved there.

## Prerequisites
- Python 3.11 or above
- Code Editor(VSCode Preferred)
- An Asana account and an Asana Personal Access Token(see instructions below)
- ngrok(see setup instructions below)

## Installation
1. Clone this repository:
Create a folder called `Dynamic_Deadline` in your System, get inside that folder and open Terminal and clone the Repository using below command.
   ```sh
   git clone https://github.com/shodhan-rai/SHODHANRAI_DYNAMICDEADLINE_VCET.git
   cd SHODHANRAI_DYNAMICDEADLINE_VCET
   ```
2. Open the folder in your code editor, for VSCode run the below command:

   ```sh
   code .
   ```

2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Set up environment variables by creating a `.env` file in the root directory and adding the below content, just make sure that you update it with actual values(instructions provided below on how to get these details):
   ```
   ASANA_ACCESS_TOKEN=<your_personal_access_token>
   ASANA_PROJECT_ID=<your_project_id>
   IN_PROGRESS_SECTION_ID=<your_in_progress_section_id>
   ```

### Steps to Get Asana Personal Access Token(ASANA_ACCESS_TOKEN):
1. Visit [Asana](https://asana.com/).
  
3. Use your email or Google account to sign up.
4. Fill in your name, role, and other necessary details.
5. Select "Create new work" and click Continue.
6. You can leave the project name blank (it defaults to "Cross-functional project plan") and click Continue.
7. You can add your own tasks or go with the default tasks provided, then click Continue.
8. Simply click Continue when prompted.
9. Select the Board Layout and then click Continue.
10. You can add emails of your teammates if you want, or just click Continue.
11. Click Skip for now to finish the setup.
12. Add a new section by clicking `Add Section` button, name the section as `In Progress`.
13. Click on your profile icon at the top right corner and select Settings.
14. Go to the Apps tab, scroll down, and click on View developer console.
15. Click Create new token under the "Personal access token" section.
In the popup window:
    - Name your token.
    - Agree to the ASANA API Terms.
    - Click Create Token.
16. Copy Token: A popup will appear with your token ID. Copy this token ID—this is your `ASANA_ACCESS_TOKEN (API Key)`.
17. Update `ASANA_ACCESS_TOKEN` in the `.env` file.


### Get you Project ID, In Progress section ID and IDs for priority Mapping:
1. First get your workspace id: In the below command replace `YOUR_ACCESS_TOKEN` with the actual ASANA API key. Running the above command will give you an id(gid), that gid is your WORKSPACE_ID.

   ```sh
   curl --location --request GET "https://app.asana.com/api/1.0/workspaces" --header "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```
  
2. Get `ASANA_PROJECT_ID`: Replace the `YOUR_WORKSPACE_ID` and `YOUR_ACCESS_TOKEN` with actual values in the below command. Running the below command will give you the gid, That gid is your `ASANA_PROJECT_ID`.

    ```sh
    curl --location --request GET "https://app.asana.com/api/1.0/workspaces/YOUR_WORKSPACE_ID/projects" --header "Authorization: Bearer YOUR_ACCESS_TOKEN"
    ```

3. Get `IN_PROGRESS_SECTION_ID`: Replace `YOUR_PROJECT_ID` and `YOUR_ACCESS_TOKEN` with actual values in the below command. Running the below command will give you gids for all the sections, the gid associated with In Progress section is your `IN_PROGRESS_SECTION_ID`.

    ```sh
    curl --location --request GET "https://app.asana.com/api/1.0/projects/YOUR_PROJECT_ID/sections" --header "Authorization: Bearer YOUR_ACCESS_TOKEN"
    ```

4. Get IDs for different priority levels(Low, Mid and High): Kindly replace {your_personal_access_token} and {project_id} with actual values in the below command. When you run the command below, you will get IDs for different priority levels. Kindly update those IDs in `webhook_listener.py`

    ```sh
    curl -H "Authorization: Bearer {your_personal_access_token}" https://app.asana.com/api/1.0/projects/{project_id}/custom_field_settings | python -c "import sys, json; data = json.load(sys.stdin);       print([{opt['gid']: opt['name']} for field in data['data'] if field['custom_field']['name'] == 'Priority' for opt in field['custom_field']['enum_options']])"
    ```

After you get  `ASANA_PROJECT_ID` and `IN_PROGRESS_SECTION_ID`, update those values in `.env` file.

### Steps to setup ngrok:
1. Install ngrok
    ```sh
    pip install ngrok
    ```

2. [ngrok account setup](https://dashboard.ngrok.com/get-started/your-authtoken)
   Sign up or Sign in using your email or Google, Agree to Terms and click Create Account

3. It will ask you to add multi-factor authentication, you can add it or skip it.
4. Click continue if skipped.
5. Now it will ask you some details, you can provide the datails or simply click continue.
6. Navigate [here](https://dashboard.ngrok.com/get-started/your-authtoken), copy your authtoken
7. Run the below command, replace `YOUR_AUTH_TOKEN` with actual authtoken.
   ```sh
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```

## Usage
1. Run the `webhook_listener.py` to start the Flask server that listens for Asana webhook events:
   ```sh
   python -u webhook_listener.py
   ```
2. Open another terminal window and run ngrok. (Replace the Port number 5000 with actual port number where your flask server is running if it is not running on port 5000).
   ```sh
   ngrok http 5000
   ```
3. Running the above command will give you a public url, copy that url and replace it in the place of `<your-ngrok-url>` at line 12 of `create_webhook.py` and save the file.

4. Run the `create_webhook.py` to create a webhook that monitors the asana for any events and sends it to Flask server:
   ```sh
   python -u create_webhook.py
   ```
3. Add tasks to Asana and test the automation by assigning priorities and moving tasks to the "In Progress" section.

## File Structure
- `webhook_listener.py`: Main Flask server to handle webhook events.
- `api.py`: Contains functions for interacting with the Asana API.
- `create_webhook.py`: Script to create webhooks in Asana.
- `config.py`: Configuration file for API settings.
- `requirements.txt`: Lists project dependencies.
