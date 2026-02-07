import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

print(f"Listing Models for Key: {api_key[:10]}...")
response = requests.get(url)

if response.status_code == 200:
    models = response.json().get('models', [])
    print("Available Models:")
    for m in models:
        if 'generateContent' in m.get('supportedGenerationMethods', []):
            print(f"- {m['name']}")
else:
    print(f"Error {response.status_code}: {response.text}")
