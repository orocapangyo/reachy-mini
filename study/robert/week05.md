## 5주차: 센서 활용 - 마이크 및 스피커

### 학습 목표

- 마이크를 통한 음성 입력 처리
- 스피커를 통한 오디오 출력
- 간단한 음성 인식 구현

---

### 1. Reachy Mini의 오디오 시스템 이해

Reachy Mini는 마이크 어레이와 스피커를 통해 음성 기반 상호작용을 지원합니다. 이를 통해 로봇이 사용자의 음성을 인식하고, 음성으로 응답하는 자연스러운 대화형 인터페이스를 구현할 수 있습니다.

#### 1.1 마이크 어레이 사양 및 특징

*   **하드웨어**: Seeed Studio reSpeaker XMOS XVF3800 기반
*   **마이크 개수**: 4개의 PDM MEMS 디지털 마이크
*   **샘플링 레이트**: 최대 16 kHz
*   **감도**: -26 dB FS
*   **신호 대 잡음비(SNR)**: 64 dBA
*   **특징**: 다중 마이크 어레이를 통해 방향 탐지 및 노이즈 제거 기능 제공

#### 1.2 스피커 사양 및 특징

*   **출력**: 5W @ 4Ohms
*   **용도**: 음성 피드백, 알림음, TTS(Text-to-Speech) 출력

#### 1.3 오디오 시스템 구성도

```
┌─────────────────────────────────────────────────────────┐
│                   Reachy Mini 오디오 시스템              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐     ┌─────────────┐     ┌───────────┐ │
│  │  4x MEMS    │────▶│   XMOS      │────▶│  USB-C    │ │
│  │  마이크      │     │  XVF3800    │     │  인터페이스 │ │
│  └─────────────┘     └─────────────┘     └───────────┘ │
│                                                ▼        │
│                                         ┌───────────┐  │
│  ┌─────────────┐                        │   Host    │  │
│  │   5W 스피커  │◀───────────────────────│  Computer │  │
│  │   @ 4Ohms   │                        └───────────┘  │
│  └─────────────┘                                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### 2. 마이크를 통한 음성 입력 처리

Python에서 마이크 입력을 처리하기 위해 `pyaudio` 또는 `sounddevice` 라이브러리를 사용할 수 있습니다.

#### 2.1 필요 라이브러리 설치

```bash
uv add pyaudio sounddevice numpy scipy
```

> [!NOTE]
> Windows에서 `pyaudio` 설치 시 오류가 발생하면 `pipwin`을 사용하세요:
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```

#### 2.2 마이크 장치 확인

시스템에 연결된 오디오 장치 목록을 확인하는 코드입니다.

```python
import sounddevice as sd

# 사용 가능한 오디오 장치 목록 출력
print("사용 가능한 오디오 장치:")
print(sd.query_devices())

# 기본 입력/출력 장치 확인
print(f"\n기본 입력 장치: {sd.query_devices(kind='input')}")
print(f"기본 출력 장치: {sd.query_devices(kind='output')}")
```

#### 2.3 실시간 마이크 입력 녹음

마이크에서 음성을 녹음하고 WAV 파일로 저장하는 예제입니다.

```python
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

# 녹음 설정
SAMPLE_RATE = 16000  # Reachy Mini 마이크 최대 샘플레이트
DURATION = 5  # 녹음 시간 (초)
CHANNELS = 1  # 모노 녹음

print(f"{DURATION}초 동안 녹음을 시작합니다...")

# 녹음 수행
audio_data = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype='int16'
)

# 녹음이 완료될 때까지 대기
sd.wait()

print("녹음이 완료되었습니다.")

# WAV 파일로 저장
output_filename = "recorded_audio.wav"
write(output_filename, SAMPLE_RATE, audio_data)
print(f"오디오가 '{output_filename}'에 저장되었습니다.")
```

#### 2.4 실시간 오디오 스트림 처리

실시간으로 마이크 입력을 처리하는 콜백 기반 예제입니다.

```python
import sounddevice as sd
import numpy as np

SAMPLE_RATE = 16000
BLOCK_SIZE = 1024  # 한 번에 처리할 샘플 수

def audio_callback(indata, frames, time, status):
    """실시간 오디오 입력 콜백 함수"""
    if status:
        print(f"상태: {status}")
    
    # 입력 오디오의 볼륨 레벨 계산 (RMS)
    volume_norm = np.linalg.norm(indata) * 10
    
    # 볼륨 레벨을 시각적으로 표시
    bar = '█' * int(volume_norm)
    print(f"\r볼륨: {bar:<50}", end='', flush=True)

print("실시간 오디오 모니터링을 시작합니다. Ctrl+C로 종료하세요.")

try:
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        channels=1,
        callback=audio_callback
    ):
        while True:
            sd.sleep(100)
except KeyboardInterrupt:
    print("\n오디오 모니터링을 종료합니다.")
```

---

### 3. 스피커를 통한 오디오 출력

#### 3.1 WAV 파일 재생

저장된 오디오 파일을 스피커로 재생하는 예제입니다.

```python
import sounddevice as sd
from scipy.io.wavfile import read

# WAV 파일 읽기
sample_rate, audio_data = read("recorded_audio.wav")

print(f"재생 중... (샘플레이트: {sample_rate} Hz)")

# 오디오 재생
sd.play(audio_data, sample_rate)

# 재생이 완료될 때까지 대기
sd.wait()

print("재생이 완료되었습니다.")
```

#### 3.2 사인파 톤 생성 및 재생

프로그래밍으로 사운드를 생성하여 재생하는 예제입니다.

```python
import sounddevice as sd
import numpy as np

SAMPLE_RATE = 44100  # CD 품질 샘플레이트
DURATION = 1.0  # 재생 시간 (초)

def generate_tone(frequency, duration, sample_rate):
    """특정 주파수의 사인파 생성"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(2 * np.pi * frequency * t)
    # 16비트 정수로 변환
    audio = (tone * 32767).astype(np.int16)
    return audio

# 다양한 음계 재생
notes = {
    'C4': 261.63,
    'D4': 293.66,
    'E4': 329.63,
    'F4': 349.23,
    'G4': 392.00,
    'A4': 440.00,
    'B4': 493.88,
    'C5': 523.25
}

print("음계를 재생합니다...")

for note_name, frequency in notes.items():
    print(f"재생 중: {note_name} ({frequency} Hz)")
    tone = generate_tone(frequency, 0.5, SAMPLE_RATE)
    sd.play(tone, SAMPLE_RATE)
    sd.wait()

print("재생이 완료되었습니다.")
```

#### 3.3 Text-to-Speech (TTS) 구현

텍스트를 음성으로 변환하여 스피커로 출력하는 예제입니다.

```bash
uv add pyttsx3 gTTS playsound
```

**pyttsx3 사용 (오프라인 TTS)**

```python
import pyttsx3

# TTS 엔진 초기화
engine = pyttsx3.init()

# 음성 속성 설정
engine.setProperty('rate', 150)    # 말하기 속도 (기본값: 200)
engine.setProperty('volume', 0.9)  # 볼륨 (0.0 ~ 1.0)

# 사용 가능한 음성 목록 확인
voices = engine.getProperty('voices')
for idx, voice in enumerate(voices):
    print(f"{idx}: {voice.name} - {voice.languages}")

# 한국어 음성이 있으면 선택 (시스템에 따라 다름)
# engine.setProperty('voice', voices[1].id)

# 텍스트를 음성으로 변환하여 재생
text = "안녕하세요, 저는 리치 미니입니다."
print(f"말하는 중: {text}")
engine.say(text)
engine.runAndWait()

print("TTS 재생이 완료되었습니다.")
```

**gTTS 사용 (온라인 TTS - 한국어 지원)**

```python
from gtts import gTTS
import os

# 한국어 텍스트
text = "안녕하세요, 저는 리치 미니입니다. 만나서 반갑습니다."

# gTTS로 음성 생성 (한국어)
tts = gTTS(text=text, lang='ko', slow=False)

# MP3 파일로 저장
output_file = "greeting.mp3"
tts.save(output_file)
print(f"음성 파일이 '{output_file}'에 저장되었습니다.")

# 파일 재생 (시스템에 따라 다른 방법 사용)
# Windows
os.system(f"start {output_file}")
# macOS: os.system(f"afplay {output_file}")
# Linux: os.system(f"mpg123 {output_file}")
```

---

### 4. 간단한 음성 인식 구현

#### 4.1 SpeechRecognition 라이브러리 설치

```bash
uv add SpeechRecognition
```

#### 4.2 음성 인식 기본 예제

마이크에서 음성을 인식하여 텍스트로 변환하는 예제입니다.

```python
import speech_recognition as sr

# 음성 인식기 초기화
recognizer = sr.Recognizer()

# 마이크에서 음성 입력 받기
with sr.Microphone() as source:
    print("주변 소음을 분석 중...")
    recognizer.adjust_for_ambient_noise(source, duration=1)
    
    print("말씀하세요...")
    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
    
print("인식 중...")

try:
    # Google Speech Recognition API 사용 (무료, 인터넷 필요)
    text = recognizer.recognize_google(audio, language='ko-KR')
    print(f"인식 결과: {text}")
except sr.UnknownValueError:
    print("음성을 인식할 수 없습니다.")
except sr.RequestError as e:
    print(f"Google Speech Recognition 서비스 오류: {e}")
```

#### 4.3 음성 인식 엔진 비교

| 특성 | Google Speech | Whisper (OpenAI) | Vosk | Sphinx |
|------|---------------|------------------|------|--------|
| **정확도** | ⭐⭐⭐ 높음 | ⭐⭐⭐ 매우 높음 | ⭐⭐ 보통 | ⭐ 낮음 |
| **오프라인** | ❌ 불가능 | ✅ 가능 | ✅ 가능 | ✅ 가능 |
| **한국어 지원** | ✅ 우수 | ✅ 우수 | ✅ 가능 | ❌ 제한적 |
| **속도** | ⭐⭐⭐ 빠름 | ⭐⭐ 보통 | ⭐⭐⭐ 빠름 | ⭐⭐ 보통 |
| **비용** | 무료 제한 | 무료 (로컬) | 무료 | 무료 |
| **설치** | 인터넷만 필요 | 모델 다운로드 | 모델 다운로드 | 복잡 |

#### 4.4 Whisper를 이용한 고급 음성 인식

OpenAI의 Whisper 모델을 사용한 오프라인 음성 인식 예제입니다.

```bash
uv add openai-whisper
```

```python
import whisper
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import tempfile
import os

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

def transcribe_audio(audio_data, sample_rate):
    """Whisper로 음성을 텍스트로 변환"""
    # 임시 WAV 파일 생성
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_path = f.name
        # float32를 int16으로 변환하여 저장
        audio_int16 = (audio_data * 32767).astype(np.int16)
        write(temp_path, sample_rate, audio_int16)
    
    try:
        # Whisper로 음성 인식
        result = model.transcribe(temp_path, language='ko')
        return result['text']
    finally:
        # 임시 파일 삭제
        os.unlink(temp_path)

# 메인 실행
print("\n음성 인식을 시작합니다.")
audio = record_audio(DURATION, SAMPLE_RATE)
text = transcribe_audio(audio, SAMPLE_RATE)
print(f"\n인식 결과: {text}")
```

---

### 5. 통합 예제: 음성 대화 시스템

마이크 입력, 음성 인식, TTS를 통합한 간단한 음성 대화 시스템입니다.

```python
import speech_recognition as sr
import pyttsx3
import time

class VoiceAssistant:
    def __init__(self):
        # 음성 인식기 초기화
        self.recognizer = sr.Recognizer()
        
        # TTS 엔진 초기화
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        
        # 명령어 매핑
        self.commands = {
            '안녕': self.greet,
            '시간': self.tell_time,
            '종료': self.shutdown,
        }
        
        self.running = True
    
    def speak(self, text):
        """텍스트를 음성으로 출력"""
        print(f"[리치 미니]: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen(self):
        """마이크에서 음성 입력을 받아 텍스트로 변환"""
        with sr.Microphone() as source:
            print("\n듣고 있습니다...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio, language='ko-KR')
                print(f"[사용자]: {text}")
                return text
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                return None
            except sr.RequestError:
                self.speak("음성 인식 서비스에 연결할 수 없습니다.")
                return None
    
    def greet(self):
        """인사 응답"""
        self.speak("안녕하세요! 저는 리치 미니입니다. 무엇을 도와드릴까요?")
    
    def tell_time(self):
        """현재 시간 알려주기"""
        current_time = time.strftime("%H시 %M분")
        self.speak(f"현재 시간은 {current_time}입니다.")
    
    def shutdown(self):
        """시스템 종료"""
        self.speak("안녕히 가세요!")
        self.running = False
    
    def process_command(self, text):
        """명령어 처리"""
        if text is None:
            return
        
        # 등록된 명령어 확인
        for keyword, action in self.commands.items():
            if keyword in text:
                action()
                return
        
        # 알 수 없는 명령어
        self.speak(f"'{text}'를 이해하지 못했습니다. 다시 말씀해 주세요.")
    
    def run(self):
        """메인 루프 실행"""
        self.speak("음성 대화 시스템을 시작합니다.")
        
        while self.running:
            text = self.listen()
            self.process_command(text)
        
        print("음성 대화 시스템을 종료합니다.")


if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()
```

---

### 6. Reachy Mini SDK와 연동

Reachy Mini의 오디오 기능을 SDK와 연동하여 로봇의 동작과 음성을 결합합니다.

```python
import speech_recognition as sr
import pyttsx3
from reachy_mini import ReachyMini

class ReachyVoiceControl:
    def __init__(self):
        # Reachy Mini 연결
        self.reachy = ReachyMini(localhost_only=True)
        self.reachy.enable_motors()
        
        # 음성 시스템 초기화
        self.recognizer = sr.Recognizer()
        self.tts = pyttsx3.init()
        
        # 명령어 등록
        self.commands = {
            '위': lambda: self.look_direction(0.5, 0, 0.5),
            '아래': lambda: self.look_direction(0.5, 0, 0.2),
            '왼쪽': lambda: self.look_direction(0.5, 0.3, 0.35),
            '오른쪽': lambda: self.look_direction(0.5, -0.3, 0.35),
            '앞': lambda: self.look_direction(0.5, 0, 0.35),
        }
    
    def speak(self, text):
        """음성 출력"""
        print(f"[리치]: {text}")
        self.tts.say(text)
        self.tts.runAndWait()
    
    def listen(self):
        """음성 입력"""
        with sr.Microphone() as source:
            print("명령을 기다리는 중...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=5)
                return self.recognizer.recognize_google(audio, language='ko-KR')
            except:
                return None
    
    def look_direction(self, x, y, z):
        """지정된 방향 바라보기"""
        self.reachy.look_at_world(x=x, y=y, z=z, duration=1.0)
    
    def run(self):
        """메인 루프"""
        self.speak("음성 제어 모드를 시작합니다.")
        
        while True:
            text = self.listen()
            if text is None:
                continue
            
            print(f"인식: {text}")
            
            if '종료' in text:
                self.speak("음성 제어를 종료합니다.")
                break
            
            # 방향 명령 처리
            for keyword, action in self.commands.items():
                if keyword in text:
                    self.speak(f"{keyword}을 바라봅니다.")
                    action()
                    break
            else:
                self.speak("알 수 없는 명령입니다.")


if __name__ == "__main__":
    controller = ReachyVoiceControl()
    controller.run()
```

---

### 7. 심화 학습 및 도전 과제

*   **방향 탐지**: 4개의 마이크 어레이를 활용하여 소리가 발생한 방향을 탐지하고, Reachy Mini가 해당 방향을 바라보도록 구현해 보세요.

*   **웨이크 워드**: "리치야" 또는 "헤이 리치"와 같은 웨이크 워드를 인식하여 음성 명령 모드를 활성화하는 시스템을 구현해 보세요. (참고: Picovoice Porcupine, Snowboy)

*   **감정 표현**: 음성의 톤과 속도를 조절하여 Reachy Mini가 다양한 감정을 표현하도록 TTS를 개선해 보세요.

*   **대화 AI 연동**: OpenAI GPT API 또는 다른 LLM과 연동하여 자연스러운 대화가 가능한 챗봇을 구현해 보세요.

---

### 8. 참고 자료

*   [SpeechRecognition 문서](https://pypi.org/project/SpeechRecognition/)
*   [OpenAI Whisper GitHub](https://github.com/openai/whisper)
*   [gTTS 문서](https://gtts.readthedocs.io/)
*   [pyttsx3 문서](https://pyttsx3.readthedocs.io/)
*   [sounddevice 문서](https://python-sounddevice.readthedocs.io/)
*   [Seeed Studio reSpeaker](https://wiki.seeedstudio.com/ReSpeaker_4_Mic_Array_for_Raspberry_Pi/)
