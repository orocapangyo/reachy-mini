"""
5-3.py: Whisper를 이용한 고급 음성 인식 예제
Week 05 - 섹션 4.4: Whisper를 이용한 고급 음성 인식

OpenAI의 Whisper 모델을 사용한 오프라인 음성 인식 예제입니다.

필요 라이브러리:
    uv add openai-whisper sounddevice numpy scipy

참고: 이 버전은 ffmpeg 없이 작동합니다.
"""

import whisper
import sounddevice as sd
import numpy as np

# Whisper 모델 로드 (tiny, base, small, medium, large 중 선택)
# 작은 모델일수록 빠르지만 정확도가 낮음
print("Whisper 모델을 로드 중...")
model = whisper.load_model("base")

SAMPLE_RATE = 16000
DURATION = 5


def record_audio(duration, sample_rate):
    """마이크에서 오디오 녹음"""
    print(f"{duration}초 동안 녹음합니다...")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    print("녹음 완료!")
    return audio.flatten()


def transcribe_audio(audio_data):
    """Whisper로 음성을 텍스트로 변환
    
    ffmpeg 없이 numpy 배열을 직접 Whisper에 전달합니다.
    """
    # Whisper는 float32 numpy 배열을 직접 처리할 수 있음
    # 오디오 데이터가 [-1.0, 1.0] 범위의 float32인지 확인
    audio_data = audio_data.astype(np.float32)
    
    # Whisper로 음성 인식 (numpy 배열 직접 전달)
    result = model.transcribe(audio_data, language='ko', fp16=False)
    return result['text']


# 메인 실행
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("Week 05 - 4.4절: Whisper를 이용한 고급 음성 인식")
    print("=" * 50)
    
    print("\n음성 인식을 시작합니다.")
    audio = record_audio(DURATION, SAMPLE_RATE)
    text = transcribe_audio(audio)
    print(f"\n인식 결과: {text}")
