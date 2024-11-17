import os
from dotenv import load_dotenv

load_dotenv()

ASANA_API_KEY = os.getenv('ASANA_API_KEY')
ASANA_PROJECT_ID = os.getenv('ASANA_PROJECT_ID')
ASANA_API_URL = "https://app.asana.com/api/1.0"
HEADERS = {
    "Authorization": f"Bearer {ASANA_API_KEY}",
    "Content-Type": "application/json"
}
