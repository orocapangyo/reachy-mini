import requests
import os

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = "facebook/mms-tts-eng"
# Try without hf-inference prefix
API_URL = f"https://router.huggingface.co/models/{MODEL_ID}"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}
payload = {"inputs": "Hello, this is a test."}

response = requests.post(API_URL, headers=headers, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}")
