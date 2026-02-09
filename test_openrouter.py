import os
from dotenv import load_dotenv
from openai import OpenAI
from utils.openrouter_config import get_openrouter_model_text, get_openrouter_headers

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
print(f"Checking API Key: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("No OPENROUTER_API_KEY found in .env")
    exit()

client = OpenAI(base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"), api_key=api_key)

try:
    model_name = get_openrouter_model_text()
    print(f"Attempting to connect to {model_name}...")
    response = client.chat.completions.create(
        model=model_name,
        extra_headers=get_openrouter_headers(),
        messages=[{"role": "user", "content": "Are you working?"}]
    )
    print(f"Success! Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"OpenRouter failed: {e}")
