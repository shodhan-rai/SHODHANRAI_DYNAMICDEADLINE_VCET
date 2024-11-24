import os
from dotenv import load_dotenv

load_dotenv()

ASANA_API_KEY = os.getenv('ASANA_API_KEY')
ASANA_PROJECT_ID = os.getenv('ASANA_PROJECT_ID')
ASANA_API_URL = os.getenv('ASANA_API_URL')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
HEADERS = {
    "Authorization": f"Bearer {ASANA_API_KEY}",
    "Content-Type": "application/json"
}
