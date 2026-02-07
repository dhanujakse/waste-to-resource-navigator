import os
import google.generativeai as genai
from dotenv import load_dotenv
from utils.gemini_config import get_gemini_model_name

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"Checking API Key: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("No API Key found in .env")
    exit()

genai.configure(api_key=api_key)

try:
    print("Listing available Gemini models...")
    models = genai.list_models()
    available = [m.name for m in models if "generateContent" in (m.supported_generation_methods or [])]
    for m in available:
        print(f"- {m}")

    model_name = get_gemini_model_name()
    print(f"Attempting to connect to {model_name}...")
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Are you working?")
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"Gemini failed: {e}")
    print("Diagnosis: API key may be invalid, not enabled, or missing access to models.")
