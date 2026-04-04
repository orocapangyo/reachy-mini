from gradio_client import Client
import os
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

client = Client("mrfakename/MeloTTS", token=HF_TOKEN)
# 인자 없이 /load_speakers 호출하거나 언어를 지정해서 확인
result = client.predict(language="KR", text="", api_name="/load_speakers")
print(result)
