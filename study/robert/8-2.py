"""
Example 8-2: hexgrad/Kokoro-82M 모델을 활용한 TTS 및 재생
Hugging Face Spaces API (Gradio Client) 활용
"""
from gradio_client import Client
import os
import shutil
import sounddevice as sd
import soundfile as sf
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 1. 허깅페이스 API 토큰 설정
# .env 파일에 HF_TOKEN이 설정되어 있어야 합니다.
HF_TOKEN = os.getenv("HF_TOKEN")

def play_sound(file_path):
    """사운드 파일 재생"""
    try:
        data, fs = sf.read(file_path)
        sd.play(data, fs)
        sd.wait()  # 재생이 끝날 때까지 대기
    except Exception as e:
        print(f"재생 오류 발생: {e}")

def generate_speech_kokoro(text, output_file="kokoro_output.wav", voice="af_heart", speed=1.0, play=True):
    """Kokoro-82M 모델을 사용한 고품질 TTS (무료/키 활용)"""
    print(f"변환 중 (Kokoro-82M via ysharma/Kokoro-TTS-mcp-test): '{text}'")
    print(f"목소리: {voice}, 속도: {speed}")
    
    try:
        # Gradio Client 연결 (Kokoro-82M 전용 스페이스)
        client = Client("ysharma/Kokoro-TTS-mcp-test", token=HF_TOKEN)
        
        # API 호출 (/generate_TTS 엔드포인트)
        # 파라미터: text, voice, speed, use_gpu
        result = client.predict(
            text=text,
            voice=voice,
            speed=speed,
            use_gpu=True, # ZeroGPU 활용
            api_name="/generate_TTS"
        )
        
        # 결과 파일 경로 (Gradio는 (audio_path, text) 튜플을 반환함)
        temp_file_path = result[0] if isinstance(result, (list, tuple)) else result
        
        # 지정된 출력 파일로 복사
        shutil.copy(temp_file_path, output_file)
        
        print(f"성공! 음성 파일이 저장되었습니다: {output_file}")
        
        if play:
            print("재생 중...")
            play_sound(output_file)
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 고품질 Kokoro-82M 테스트
    test_text = "Kokoro is an open-weight TTS model with 82 million parameters. It delivers incredible quality for its size."
    
    # 다양한 목소리 선택 가능: 
    # af_heart (여성), am_adam (남성), bf_alice (영국 여성) 등
    generate_speech_kokoro(
        text=test_text, 
        output_file="8-2_output.wav", 
        voice="af_heart", 
        speed=1.0, 
        play=True
    )
