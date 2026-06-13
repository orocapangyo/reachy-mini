import os
import sys
import numpy as np
import time
import torch
import whisper
from reachy_mini import ReachyMini

# 1. 오리지널 OpenAI Whisper 모델 로드
# 실습 환경(CPU)에서의 실시간 성능을 위해 가장 가볍고 빠른 'tiny' 모델을 사용합니다.
print("OpenAI Whisper 모델 로딩 중... (최초 구동 시 시간이 걸릴 수 있습니다)")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("tiny", device=device)
print(f"모델 로딩 완료! (사용 장치: {device})")

def listen_command_whisper(mini):
    print("\n[듣는 중...] 마이크에 대고 말씀하세요 (3초)")
    
    audio_buffer = []
    start_time = time.time()
    while time.time() - start_time < 3:
        sample = mini.media.get_audio_sample()
        if sample is not None and len(sample) > 0:
            audio_buffer.append(sample)
            
    if not audio_buffer:
        print("[주의]: 마이크 데이터가 수집되지 않았습니다.")
        return None

    # 2. 오디오 조각 결합 및 오리지널 Whisper 규격 맞추기
    audio_raw = np.concatenate(audio_buffer)
    
    # 정규화: int16 데이터를 float32 범위(-1.0 ~ 1.0)로 변환
    audio_data = audio_raw.astype(np.float32) / 32768.0
    
    # 채널 변환: Reachy Mini의 스테레오(2채널) 데이터를 모노(1채널)로 평균내기
    if len(audio_data.shape) > 1 and audio_data.shape[1] == 2:
        audio_data = np.mean(audio_data, axis=1)

    try:
        # 3. Whisper 모델로 음성 인식 수행
        # 오리지널 whisper.transcribe() 함수는 내부적으로 데이터를 PyTorch 텐서로 변환하여 처리합니다.
        print("[AI 분석 중...]")
        result = model.transcribe(audio_data, language="ko", fp16=False)
        
        text = result["text"].strip()
        print(f"[인식 결과 (Whisper)]: {text}")
        return text
    except Exception as e:
        print(f"[인식 에러]: {e}")
        return None

# 실행부
try:
    with ReachyMini() as mini:
        mini.wake_up()
        print("로봇이 준비되었습니다.")
        
        while True:
            command = listen_command_whisper(mini)
            if command:
                if "안녕" in command:
                    print("=> 로봇 동작: 반갑게 인사하기")
                    mini.look_at_image(320, 100, 0.5)  # 고개 들기
                    time.sleep(0.5)
                    mini.look_at_image(320, 240, 0.5)  # 정면
                elif "종료" in command:
                    print("실습을 종료합니다.")
                    break
            time.sleep(0.1)
except KeyboardInterrupt:
    print("사용자에 의해 종료되었습니다.")
