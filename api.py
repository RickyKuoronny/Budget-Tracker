import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

url = "https://au-api.basiq.io/token"

payload = {
    "scope": "CLIENT_ACCESS",
    "userId": os.getenv("USER_ID")  
}

headers = {
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {os.getenv('API_KEY')}"  
}

response = requests.post(url, data=payload, headers=headers)

if response.status_code == 200:
    print("Access Token:", response.json())
else:
    print("Error:", response.status_code, response.text)
