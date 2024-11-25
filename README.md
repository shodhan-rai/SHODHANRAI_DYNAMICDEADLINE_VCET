# Dynamic Deadline Automation


This project automates the assignment of due dates to tasks based on priority and extends due dates for tasks in the "In Progress" section when a high-priority task is moved to that section.

## Features
- Assigns initial due dates based on task priority:
  - Low: 14 days from the present date.
  - Mid: 7 days from the present date.
  - High: 2 days from the present date.
- Automatically extends due dates for all tasks in the "In Progress" section by 2 days when a high-priority task is moved there.
- Reduces due dates for tasks in 'In Progress' section by 2 days when high priority task is moved out of 'In Progress' section.
- Prevents redundant due date extensions and due date reductions.

## Prerequisites
- Python 3.11 or above
- Code Editor(VS Code)
- An Asana account and an Asana Personal Access Token(see instructions below)
- ngrok(see setup instructions below)

## Installation
1. Clone the repository:
Create a folder called `Dynamic_Deadline` in your System, get inside that folder and open Terminal and clone the Repository using below command.
   ```sh
   git clone https://github.com/shodhan-rai/SHODHANRAI_DYNAMICDEADLINE_VCET.git
   cd SHODHANRAI_DYNAMICDEADLINE_VCET
   ```
2. Open in Visual Studio Code:

   ```sh
   code .
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```


## File Structure
- `webhook_listener.py`: Main Flask server to handle webhook events.
- `api.py`: Contains functions for interacting with the Asana API.
- `create_webhook.py`: Script to create webhooks in Asana.
- `config.py`: Configuration file for API settings.
- `gunicorn_config.py`: Configuration file for deployment in cloud
- `requirements.txt`: Lists project dependencies.

## Configuration

## 1. Asana Setup

## Getting Your Personal Access Token
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


## Retrieving Required IDs
### Workspace ID:
In the below command replace `YOUR_ACCESS_TOKEN` with the actual ASANA API key. Running the above command will give you an id(gid), that gid is your WORKSPACE_ID.

   ```sh
   curl --location --request GET "https://app.asana.com/api/1.0/workspaces" --header "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

### Project ID:
Replace the `YOUR_WORKSPACE_ID` and `YOUR_ACCESS_TOKEN` with actual values in the below command. Running the below command will give you the gid, That gid is your `ASANA_PROJECT_ID`.

  ```sh
  curl --location --request GET "https://app.asana.com/api/1.0/workspaces/YOUR_WORKSPACE_ID/projects" --header "Authorization: Bearer YOUR_ACCESS_TOKEN"
  ```

### In Progress Section ID:
Replace `YOUR_PROJECT_ID` and `YOUR_ACCESS_TOKEN` with actual values in the below command. Running the below command will give you gids for all the sections, the gid associated with In Progress section is your `IN_PROGRESS_SECTION_ID`.

  ```sh
  curl --location --request GET "https://app.asana.com/api/1.0/projects/YOUR_PROJECT_ID/sections" --header "Authorization: Bearer YOUR_ACCESS_TOKEN"
  ```

### Priority Level IDs:
Replace `YOUR_ACCESS_TOKEN` and `YOUR_PROJECT_ID` with actual values in the below command. Kindly update those IDs in `webhook_listener.py` at line 12.

  ```sh
  curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" https://app.asana.com/api/1.0/projects/YOUR_PROJECT_ID/custom_field_settings | python -c "import sys, json; data = json.load(sys.stdin);       print([{opt['gid']: opt['name']} for field in data['data'] if field['custom_field']['name'] == 'Priority' for opt in field['custom_field']['enum_options']])"
  ```

## 2. Environment Setup
1. Create a `.env` file in the project root and place the below content:

   ```sh
   ASANA_ACCESS_TOKEN=<your_personal_access_token>
   ASANA_PROJECT_ID=<your_project_id>
   IN_PROGRESS_SECTION_ID=<your_in_progress_section_id>
   ASANA_API_URL=https://app.asana.com/api/1.0
   WEBHOOK_URL=<your_ngrok_url>
   ```

2. Replace `<your_personal_access_token>`, `<your_project_id>` and `<your_in_progress_section_id>` with the correct values and save the file.

3. Set system environment variables (Windows):

   ```sh
   setx ASANA_ACCESS_TOKEN "your-personal-access-token"
   ```
   ```sh
   setx ASANA_PROJECT_ID "your-project-id"
   ```
   

## 3. ngrok Configuration
### Install ngrok:
  ```sh
  pip install ngrok
  ```
### Set up authentication:

1. [ngrok account setup](https://dashboard.ngrok.com/get-started/your-authtoken)
   Sign up or Sign in using your email or Google, Agree to Terms and click Create Account
2. It will ask you to add multi-factor authentication, you can add it or skip it.
3. Click continue if skipped.
4. Now it will ask you some details, you can provide the datails or simply click continue.
5. Navigate [here](https://dashboard.ngrok.com/get-started/your-authtoken), copy your authtoken
6. Run the below command in terminal, replace `YOUR_AUTH_TOKEN` with actual authtoken.
   
   ```sh
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```

## Before you run the Application

 1. Make sure that `.env` file has correct info and it has been saved in the root directory.
 2. Make sure that you have set the system variables correctly.
 3. Make sure that you have updated the Priority Level IDs in `webhook_listener.py` line 12.
 4. Make sure that ngrok is configured correctly

   
## Running the Application
1. Start the Flask server:
   ```sh
   python -u webhook_listener.py
   ```
2. In a new terminal, start ngrok:
   ```sh
   ngrok http 5000
   ```
3. Running the above command will give you a public url, copy that url and replace it in the place of `<your-ngrok-url>` at line 5 of `.env` and save the file.

4. In a new terminal, create the webhook:
   ```sh
   python -u create_webhook.py
   ```

## Testing
1. Create tasks in your Asana project
2. Assign different priority levels to tasks
3. Move tasks to the "In Progress" section
4. Verify that due dates are being set and updated according to the rules
5. Remove the high priority task from In Progress section
6. Verify that due dates of tasks in 'In Progress' section gets reduced
7. Verify that no duplicate due date extensions and reductions are being made


## Demonstration video for updated requirements
[Watch the Demonstration Video](https://drive.google.com/file/d/156TLunMzLU2VpGjikhQOSl9PeGfrdUqr/view?usp=sharing)

### For example inputs refer [EXAMPLES.md](https://github.com/shodhan-rai/SHODHANRAI_DYNAMICDEADLINE_VCET/blob/main/EXAMPLES.md)

### For Working Info refer [WORKING_INFO.md](https://github.com/shodhan-rai/SHODHANRAI_DYNAMICDEADLINE_VCET/blob/main/WORKING_INFO.md)

### To see the working in real time, I have granted access to the asana project where you can verify the working
- Check your email and accept the invite
