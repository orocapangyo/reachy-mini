import requests
import os

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = "hexgrad/Kokoro-82M"
# OpenAI compatible endpoint
API_URL = "https://router.huggingface.co/hf-inference/v1/audio/speech"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}
payload = {
    "model": MODEL_ID,
    "input": "Hello, this is a test of the OpenAI compatible TTS endpoint.",
    "voice": "af_heart"
}

response = requests.post(API_URL, headers=headers, json=payload)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    with open("test_openai.mp3", "wb") as f:
        f.write(response.content)
    print("Success! Saved to test_openai.mp3")
else:
    print(f"Response: {response.text}")
