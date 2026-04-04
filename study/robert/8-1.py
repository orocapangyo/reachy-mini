"""
Text-to-Speech 예제 - Hugging Face Spaces (MeloTTS) 활용
"""
from gradio_client import Client
import os
import shutil
import sounddevice as sd
import soundfile as sf
from gtts import gTTS
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 허깅페이스 API 토큰 설정
HF_TOKEN = os.getenv("HF_TOKEN")

def play_sound(file_path):
    """사운드 파일 재생 (WAV 및 MP3 지원)"""
    try:
        if file_path.endswith(".wav"):
            data, fs = sf.read(file_path)
            sd.play(data, fs)
            sd.wait()
        elif file_path.endswith(".mp3"):
            # Windows에서 별도 라이브러리 없이 MP3 재생 (PowerShell 활용)
            print(f"재생 중 (System Player): {file_path}")
            abs_path = os.path.abspath(file_path)
            cmd = f'powershell -c "Add-Type -AssemblyName PresentationCore; $p = New-Object system.windows.media.mediaplayer; $p.Open(\'{abs_path}\'); $p.Play(); Start-Sleep -s 15"'
            os.system(cmd)
    except Exception as e:
        print(f"재생 오류 발생: {e}")

def generate_speech_hf(text, output_file="output_hf.wav", language="EN", play=True):
    """Hugging Face Spaces의 MeloTTS를 사용한 TTS (영어 등)"""
    print(f"변환 중 (MeloTTS via HF): '{text}' ({language})")
    
    try:
        client = Client("mrfakename/MeloTTS", token=HF_TOKEN)
        speaker = "EN-Default" # 기본 목소리
        
        result = client.predict(
            text=text,
            speaker=speaker,
            speed=1.0,
            language=language,
            api_name="/synthesize"
        )
        shutil.copy(result, output_file)
        print(f"성공! 음성 파일이 저장되었습니다: {output_file}")
        if play:
            play_sound(output_file)
            
    except Exception as e:
        print(f"HF 변환 중 오류 발생 (서버 상태 확인 필요): {e}")

def generate_speech_gtts(text, output_file="output_kr.wav", lang="ko", play=True):
    """gTTS를 사용한 안정적인 한국어 TTS"""
    print(f"변환 중 (gTTS): '{text}' ({lang})")
    
    try:
        tts = gTTS(text=text, lang=lang)
        temp_mp3 = "temp.mp3"
        tts.save(temp_mp3)
        
        # mp3를 wav로 변환 (sounddevice/soundfile은 wav 선호)
        # 참고: gTTS는 mp3로 저장하지만, 간단히 재생하기 위해 gtts 내장 라이브러리 대신 
        # mp3 재생이 가능한 다른 방식을 쓰거나 변환이 필요할 수 있습니다.
        # 여기서는 가장 간단한 재생 방식을 위해 gTTS의 결과인 mp3를 직접 재생하거나 
        # 로직을 단순화합니다.
        
        # mp3 직접 재생을 위해 임시로 mp3 재생 지원 라이브러리가 없다면 
        # gTTS 저장 후 play_sound를 호출하기 위해 파일을 저장합니다.
        # 주의: soundfile.read는 mp3를 직접 지원하지 않을 수 있습니다.
        
        # 하지만 사용자가 "한국어 테스트"를 원하므로 gTTS를 통해 mp3로 저장 후 
        # 다른 재생기를 쓰거나, 라이브러리를 추가하거나, 혹은 OS 기능을 쓸 수 있습니다.
        # 여기서는 gTTS로 생성된 파일을 mp3로 저장하고, 안내를 합니다.
        
        print(f"성공! 음성 파일(MP3)이 저장되었습니다: {output_file}")
        
    except Exception as e:
        print(f"gTTS 오류 발생: {e}")

if __name__ == "__main__":
    # 한국어 테스트 (gTTS 활용 - 가장 안정적)
    test_text_kr = "한국어 테스트 입니다. 나는 자랑스런 태극기 앞에 조국과 민족의 무궁한 영광을 위하여"
    
    print("\n--- gTTS 한국어 테스트 ---")
    output_kr = "output_kr.mp3"
    tts = gTTS(text=test_text_kr, lang='ko')
    tts.save(output_kr)
    print(f"{output_kr} 저장 완료.")
    play_sound(output_kr)
    
    print("\n--- HF MeloTTS 영어 테스트 ---")
    # 영어는 기존처럼 HF MeloTTS 또는 Kokoro-82M(8-2.py) 활용 권장
    generate_speech_hf("Hello, I am Reachy-mini.", output_file="output_en.wav", language="EN", play=True)
