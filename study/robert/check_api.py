from gradio_client import Client
import os

HF_TOKEN = os.getenv("HF_TOKEN")
client = Client("Pendrokar/Kokoro-TTS", token=HF_TOKEN)
client.view_api()
