import os
import sys
import tempfile
import requests
import speech_recognition as sr
import contextlib
from gtts import gTTS
import pygame
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import noisereduce as nr
import soundfile as sf
import torch

# ========== 설정 ==========
USE_GPU = torch.cuda.is_available()
DEVICE = 0 if USE_GPU else -1
WAKE_WORDS = ["헬로", "hi", "하이", "안녕"]
EXIT_WORDS = ["없어", "됐어", "아니"]
MUSIC_PATH = "/home/naseungwon/reachy_mini/no-copyright-music-1.mp3"

# ========== 초기화 ==========
pygame.mixer.init()

print("🧠 Whisper-large-v3 모델 로딩 중...")
stt_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3", device=DEVICE)

model_id = "google/flan-t5-base"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
llm = pipeline("text2text-generation", model=model, tokenizer=tokenizer)

# ========== 유틸 함수 ==========
def suppress_stderr_globally():
    sys.stderr = open(os.devnull, 'w')

@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull, 'w') as fnull:
        stderr = sys.stderr
        sys.stderr = fnull
        try:
            yield
        finally:
            sys.stderr = stderr

# ========== 음성 입력 ==========
def listen_audio(timeout=10, phrase_time_limit=5, filename="input.wav"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 음성을 듣고 있어요...")
        with suppress_stderr():
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            with open(filename, "wb") as f:
                f.write(audio.get_wav_data())
            print(f"✅ 저장 완료: {filename}")
    return filename

def clean_audio(input_path="input.wav", output_path="cleaned.wav"):
    try:
        data, rate = sf.read(input_path)
        reduced = nr.reduce_noise(y=data, sr=rate)
        sf.write(output_path, reduced, rate)
        print(f"🔇 노이즈 제거 완료 → {output_path}")
        return output_path
    except Exception as e:
        print("❌ 노이즈 제거 실패:", e)
        return input_path

def transcribe_audio(filename="cleaned.wav"):
    result = stt_pipeline(filename)
    print("📝 인식된 텍스트:", result['text'])
    return result['text'].strip()

# ========== 텍스트 응답 생성 ==========
def generate_response(text):
    prompt = f"질문: {text.strip()}\n대답:"
    result = llm(prompt, max_new_tokens=100)
    response = result[0]["generated_text"].strip()
    return response if response else "죄송해요, 잘 이해하지 못했어요."

# ========== 음성 출력 ==========
def speak(text, lang='ko'):
    if not text.strip():
        print("⚠️ 음성으로 출력할 텍스트가 없습니다.")
        return
    print(f"🗣 응답: {text}")
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        pygame.mixer.music.load(fp.name)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pass

# ========== 음악 재생 ==========
music_state = "stopped"  # 상태: "playing", "paused", "stopped"

def play_music():
    if os.path.exists(MUSIC_PATH):
        pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.play()
        print("🎵 음악 재생 중...")
    else:
        speak("죄송해요, 음악 파일을 찾을 수 없어요.")

def stop_music():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        print("⏹ 음악 꺼짐")

def speak_nonblocking(text, lang='ko'):
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        sound = pygame.mixer.Sound(fp.name)
        ch = pygame.mixer.find_channel()
        if ch:
            ch.play(sound)

# ========== 날씨 정보 ==========
def get_weather(city="Seoul"):
    API_KEY = "5d17af980c9cf48721b0e57c1b4fedaf"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&lang=kr&units=metric"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"{city}의 현재 날씨는 {desc}, 기온은 {temp:.1f}도입니다."
    else:
        return "날씨 정보를 가져오는 데 실패했어요."

# ========== 메인 루프 ==========
def main():
    suppress_stderr_globally()
    print("🤖 '헬로 미니'를 기다리는 중입니다...")

    # [1] 웨이크 워드 대기
    while True:
        path = listen_audio()
        cleaned = clean_audio(path)
        transcript = transcribe_audio(cleaned).lower()
        if any(transcript.startswith(wake) or transcript == wake for wake in WAKE_WORDS):
            speak("안녕하세요! 무엇을 도와드릴까요?")
            break

    # [2] 명령 처리 루프 (지속적으로 명령 수용)
    while True:
        path = listen_audio()
        cleaned = clean_audio(path)
        user_text = transcribe_audio(cleaned).lower()

        if any(bye in user_text for bye in EXIT_WORDS):
            speak("프로그램을 종료합니다.")
            break

        # 명령 처리
        if "날씨" in user_text:
            response = get_weather()
            speak(response)

        elif "음악" in user_text or "노래" in user_text:
            speak("음악을 재생할게요.")
            play_music()

            # 음악 재생 중 멈춤 감지 루프
            while True:
                path = listen_audio()
                cleaned = clean_audio(path)
                cmd = transcribe_audio(cleaned).lower()
                if "꺼줘" in cmd:
                    stop_music()
                    speak("음악을 끌게요.")
                    break
                else:
                    speak_nonblocking("죄송해요, 잘 못 알아 들었어요.")
                    # 음악 계속 유지 (중단 안 됨!)

        else:
            response = generate_response(user_text)
            speak(response)

        # 다음 질문 유도
        speak("더 필요한 거 있으신가요?")


if __name__ == "__main__":
    main()
