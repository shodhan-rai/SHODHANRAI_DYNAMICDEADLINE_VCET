# Dynamic Deadline Automation with Asana


This project automates the assignment of due dates to tasks based on priority and extends due dates for tasks in the "In Progress" section when a high-priority task is moved to that section.

## Features
- Assigns initial due dates based on task priority:
  - Low: 14 days from the present date.
  - Mid: 7 days from the present date.
  - High: 2 days from the present date.
- Automatically extends due dates for all tasks in the "In Progress" section by 2 days when a high-priority task is moved there.

## Requirements
- Python 3.11 or above
- An Asana account and an Asana Personal Access Token
- Setup ngrok
### Steps to setup ngrok
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
7. Run the below command, replace YOUR_AUTH_TOKEN with actual authtoken.
   ```sh
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```

### Steps to Get Asana Personal Access Token
1. Visit [Asana](https://asana.com/).
2. Use your email or Google account to sign up.
3. Fill in your name, role, and other necessary details.
4. Select "Create new work" and click Continue.
5. You can leave the project name blank (it defaults to "Cross-functional project plan") and click Continue.
6. You can add your own tasks or go with the default tasks provided, then click Continue.
7. Simply click Continue when prompted.
8. Select the Board Layout and then click Continue.
9. You can add emails of your teammates if you want, or just click Continue.
10. Click Skip for now to finish the setup.
11. Add a new section by clicking Add Section button, name the section as In Progress.
12. Click on your profile icon at the top right corner and select Settings.
13. Go to the Apps tab, scroll down, and click on View developer console.
14. Click Create new token under the "Personal access token" section.
In the popup window:
    - Name your token.
    - Agree to the ASANA API Terms.
    - Click Create Token.
15. Copy Token: A popup will appear with your token ID. Copy this token ID—this is your Asana Personal Access Token (API Key).


## Get you Project ID, In Progress section ID and IDs for priority Mapping
1. First get your workspace id: In the below command replace YOUR_ACCESS_TOKEN with the actual ASANA API key. Running the above command will give you your workspace id(gid), that gid is your WORKSPACE_ID.

   ```sh
   curl --location --request GET "https://app.asana.com/api/1.0/workspaces" --header "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```
  
2. Get `ASANA_PROJECT_ID`: Replace the YOUR_WORKSPACE_ID and YOUR_ACCESS_TOKEN with actual values in the below command. Running the below command will give you the gid, That gid is your ASANA_PROJECT_ID.

    ```sh
    curl --location --request GET "https://app.asana.com/api/1.0/workspaces/YOUR_WORKSPACE_ID/projects" --header "Authorization: Bearer YOUR_ACCESS_TOKEN"
    ```

3. Get `IN_PROGRESS_SECTION_ID`: Replace YOUR_PROJECT_ID and YOUR_ACCESS_TOKEN with actual values in the below command. Running the below command will give you gids for all the sections, the gid associated with In Progress section is your IN_PROGRESS_SECTION_ID.

    ```sh
    curl --location --request GET "https://app.asana.com/api/1.0/projects/YOUR_PROJECT_ID/sections" --header "Authorization: Bearer YOUR_ACCESS_TOKEN"
    ```

4. Get IDs for different priority levels(Low, Mid and High): Kindly replace {your_personal_access_token} and {project_id} with actual values in the below command. When you run the command below, you will get IDs for different priority levels. Kindly update those IDs in `webhook_listener.py`

    ```sh
    curl -H "Authorization: Bearer {your_personal_access_token}" https://app.asana.com/api/1.0/projects/{project_id}/custom_field_settings | python -c "import sys, json; data = json.load(sys.stdin);       print([{opt['gid']: opt['name']} for field in data['data'] if field['custom_field']['name'] == 'Priority' for opt in field['custom_field']['enum_options']])"
    ```

After you get `ASANA_PROJECT_ID` and `IN_PROGRESS_SECTION_ID`, update those values in `.env` file.

## Installation
1. Clone this repository:
Create a folder called Dynamic_Deadline in your System and inside that folder open Terminal / Command Prompt and clone the Repo
   ```sh
   git clone https://github.com/shodhan-rai/SHODHANRAI_DYNAMICDEADLINE_VCET.git
   cd SHODHANRAI_DYNAMICDEADLINE_VCET
   ```

2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Set up environment variables by creating a `.env` file in the root directory and adding the below content, just make sure that you update it with actual values:
   ```
   ASANA_ACCESS_TOKEN=<your_personal_access_token>
   ASANA_PROJECT_ID=<your_project_id>
   IN_PROGRESS_SECTION_ID=<your_in_progress_section_id>
   ```
