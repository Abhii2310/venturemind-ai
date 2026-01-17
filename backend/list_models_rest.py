import os
import requests
import json
from dotenv import load_dotenv

load_dotenv("backend/.env")
api_key = os.getenv("GEMINI_API_KEY")

print(f"Testing Key: {api_key[:5]}...{api_key[-5:]}")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        models = response.json().get('models', [])
        print(f"Found {len(models)} models.")
        for m in models:
            print(f"- {m['name']}")
    else:
        print("Response:", response.text)
except Exception as e:
    print(f"Error: {e}")
