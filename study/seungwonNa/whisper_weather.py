from transformers import pipeline
import requests
import speech_recognition as sr
import pyttsx3
import os
import sys
import contextlib
from gtts import gTTS
import playsound
import tempfile

@contextlib.contextmanager
def suppress_stderr():
    """표준 에러 출력 억제용 컨텍스트 매니저"""
    with open(os.devnull, 'w') as fnull:
        stderr = sys.stderr
        sys.stderr = fnull
        try:
            yield
        finally:
            sys.stderr = stderr

def record_audio(filename="input.wav"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 말해주세요...")
        with suppress_stderr():
            audio = recognizer.listen(source, timeout = 10, phrase_time_limit = 5)
            with open(filename, "wb") as f:
                f.write(audio.get_wav_data())
            print(f"✅ 저장 완료: {filename}")
    return filename

# 1. Whisper로 음성 텍스트 추출
def transcribe_audio(filename="input.wav"):
    stt = pipeline("automatic-speech-recognition", model="openai/whisper-base")
    result = stt(filename)
    print("📝 인식된 텍스트:", result['text'])
    return result['text']

# 2. 날씨 API 호출
def get_weather(city="Seoul"):
    API_KEY = "개인 API Key" 
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&lang=kr&units=metric"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"{city}의 현재 날씨는 {desc}, 기온은 {temp:.1f}도입니다."
    else:
        return "날씨 정보를 가져오는 데 실패했어요."

# 3. 텍스트를 기반으로 리액션 생성
def react_to_text(text):
    if "날씨" in text:
        return get_weather()
    else:
        return "죄송해요, 아직 그 요청은 처리할 수 없어요."

def speak(text, lang='ko'):
    print("🗣 (gTTS) 음성 출력 중...")
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        playsound.playsound(fp.name)

# 4. 실행 흐름
if __name__ == "__main__":
    wav_path = record_audio()
    transcript = transcribe_audio(wav_path)
    response = react_to_text(transcript)
    print("🤖 응답:", response)
    speak(response)
