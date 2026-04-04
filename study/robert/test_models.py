from huggingface_hub import InferenceClient
import os

HF_TOKEN = os.getenv("HF_TOKEN")
models = ["facebook/mms-tts-eng", "microsoft/speecht5_tts", "espnet/kan-bayashi_ljspeech_vits"]

for model in models:
    print(f"Testing model: {model}")
    try:
        client = InferenceClient(model=model, token=HF_TOKEN)
        audio = client.text_to_speech("This is a test.")
        with open(f"test_{model.split('/')[-1]}.wav", "wb") as f:
            f.write(audio)
        print(f"Success with {model}!")
        break
    except Exception as e:
        print(f"Failed {model}: {e}")
