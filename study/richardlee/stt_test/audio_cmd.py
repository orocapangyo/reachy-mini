''' 리치미니 데몬 실행중 다음 코드 실행
    위, 아래, 오른쪽, 왼쪽에 대한 명령대로  리치미니가 고개를 움직임.
    study교재 버전보다 인식율 많이 좋아짐
'''
import os
import collections
import pyaudio
import numpy as np
import onnxruntime as ort
import urllib.request
from faster_whisper import WhisperModel
import pyttsx3
import time
from reachy_mini import ReachyMini

# VAD 및 오디오 설정
FORMAT = pyaudio.paInt16       # 16-bit PCM 포맷
CHANNELS = 1                  # 모노 채널
RECORD_RATE = 44100           # 녹음용 샘플링 레이트
RATE = 16000                  # VAD & Whisper용 16kHz
TARGET_CHUNK_SIZE = 512       # 16kHz 기준 32ms
RECORD_CHUNK_SIZE = 1411      # 44.1kHz 기준 32ms

VAD_THRESHOLD = 0.4
MIN_SILENCE_MS = 600
SPEECH_PAD_MS = 100

def resample(audio, target_len):
    """numpy 선형 보간을 활용한 빠르고 왜곡 없는 다운샘플링"""
    src_indices = np.linspace(0, len(audio) - 1, target_len)
    return np.interp(src_indices, np.arange(len(audio)), audio).astype(np.float32)

class OnnxVADIterator:
    def __init__(self, model_path="silero_vad.onnx", threshold=0.5, sampling_rate=16000, min_silence_duration_ms=600, speech_pad_ms=100):
        if not os.path.exists(model_path):
            print(f"[VAD] 로컬에 VAD 모델이 없습니다. 다운로드 중: {model_path}...")
            url = "https://github.com/snakers4/silero-vad/raw/master/src/silero_vad/data/silero_vad.onnx"
            import ssl
            context = ssl._create_unverified_context()
            with urllib.request.urlopen(url, context=context) as response, open(model_path, 'wb') as out_file:
                out_file.write(response.read())
            print("[VAD] 다운로드 완료.")

        self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        self.threshold = threshold
        self.sampling_rate = sampling_rate
        self.min_silence_samples = (sampling_rate * min_silence_duration_ms) // 1000
        self.speech_pad_samples = (sampling_rate * speech_pad_ms) // 1000
        self.reset_states()
        
    def reset_states(self):
        self._state = np.zeros((2, 1, 128), dtype=np.float32)
        self._context = np.zeros((1, 64), dtype=np.float32)
        self._triggered = False
        self._temp_end = 0
        self._current_sample = 0
        self.current_prob = 0.0
        
    def __call__(self, x, return_seconds=False):
        chunk_size = len(x)
        self._current_sample += chunk_size
        input_data = x.astype(np.float32).reshape(1, -1)
        input_with_context = np.concatenate([self._context, input_data], axis=1)
        self._context = input_with_context[:, -64:]
        sr_data = np.array(self.sampling_rate, dtype=np.int64)
        
        inputs = {
            'input': input_with_context,
            'sr': sr_data,
            'state': self._state
        }
        
        output, new_state = self.session.run(None, inputs)
        self._state = new_state
        speech_prob = output[0][0]
        self.current_prob = float(speech_prob)
        
        ret = {}
        if (speech_prob >= self.threshold) and (self._temp_end > 0):
            self._temp_end = 0
            
        if (speech_prob >= self.threshold) and not self._triggered:
            self._triggered = True
            start_sample = self._current_sample - chunk_size - self.speech_pad_samples
            start_sample = max(0, start_sample)
            if return_seconds:
                ret['start'] = round(start_sample / self.sampling_rate, 2)
            else:
                ret['start'] = start_sample
                
        elif (speech_prob < self.threshold) and self._triggered:
            if self._temp_end == 0:
                self._temp_end = self._current_sample
            if self._current_sample - self._temp_end >= self.min_silence_samples:
                end_sample = self._temp_end + self.speech_pad_samples
                self._temp_end = 0
                self._triggered = False
                if return_seconds:
                    ret['end'] = round(end_sample / self.sampling_rate, 2)
                else:
                    ret['end'] = end_sample
        return ret

class ReachyVoiceControl:
    def __init__(self):
        # Reachy Mini 연결
        self.reachy = ReachyMini(localhost_only=True)
        self.reachy.enable_motors()
        
        # 1. VAD 모듈 초기화
        print("[1/2] Silero VAD ONNX 모델 로드 중...")
        self.vad_iterator = OnnxVADIterator(
            threshold=VAD_THRESHOLD,
            sampling_rate=RATE,
            min_silence_duration_ms=MIN_SILENCE_MS,
            speech_pad_ms=SPEECH_PAD_MS
        )
        print(" -> VAD 모델 로드 완료.")
        
        # 2. Faster-Whisper 모델 로드
        print("[2/2] Faster-Whisper 모델 로드 중 (CPU + int8 양자화)...")
        self.whisper_model = WhisperModel(
            model_size_or_path="tiny", 
            device="cpu", 
            compute_type="int8"
        )
        print(" -> Faster-Whisper 모델 로드 완료.")
        
        # PyAudio 초기화
        self.p = pyaudio.PyAudio()
        
        # 음성 시스템 초기화
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
        """음성 출력 (호출할 때마다 새로 생성하는 것이 SAPI5 충돌 방지에 안전함)"""
        print(f"[리치]: {text}")
        try:
            tts = pyttsx3.init()
            tts.say(text)
            tts.runAndWait()
            tts.stop()
        except Exception as e:
            print(f"TTS 재생 에러: {e}")
            
    def listen(self):
        """VAD를 통해 음성 유무 구간만 잘라내어 Faster-Whisper로 로컬 분석"""
        try:
            stream = self.p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RECORD_RATE,
                input=True,
                input_device_index=0,
                frames_per_buffer=RECORD_CHUNK_SIZE
            )
        except Exception as e:
            print(f"❌ 마이크 스트림 열기 실패: {e}")
            return None
            
        self.vad_iterator.reset_states()
        is_speaking = False
        speech_buffer = []
        pre_buffer = collections.deque(maxlen=6)
        
        print("\n명령을 기다리는 중...")
        
        start_time = time.time()
        TIMEOUT_SECONDS = 10
        
        try:
            while True:
                if not is_speaking and (time.time() - start_time > TIMEOUT_SECONDS):
                    return None
                    
                raw_data = stream.read(RECORD_CHUNK_SIZE, exception_on_overflow=False)
                audio_chunk_np_441 = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
                audio_chunk_np = resample(audio_chunk_np_441, TARGET_CHUNK_SIZE)
                
                if is_speaking:
                    speech_buffer.append(audio_chunk_np)
                else:
                    pre_buffer.append(audio_chunk_np)
                    
                speech_dict = self.vad_iterator(audio_chunk_np, return_seconds=True)
                
                if speech_dict:
                    if 'start' in speech_dict:
                        is_speaking = True
                        speech_buffer = list(pre_buffer) + [audio_chunk_np]
                        pre_buffer.clear()
                        print("[VAD] 🗣️ 입력 중...")
                        
                    if 'end' in speech_dict:
                        is_speaking = False
                        print("[VAD] 🔇 대화 종료 감지. 명령 분석 중...")
                        break
        except Exception as e:
            print(f"음성 입력 오류: {e}")
            return None
        finally:
            stream.stop_stream()
            stream.close()
            
        if len(speech_buffer) > 0:
            audio_data = np.concatenate(speech_buffer)
            if len(audio_data) >= RATE * 0.5:
                try:
                    segments, info = self.whisper_model.transcribe(
                        audio_data,
                        beam_size=5,
                        language="ko",
                        vad_filter=False
                    )
                    text = "".join([segment.text for segment in segments]).strip()
                    if text:
                        return text
                except Exception as e:
                    print(f"STT 오류: {e}")
                    
        return None
        
    def look_direction(self, x, y, z):
        """지정된 방향 바라보기"""
        self.reachy.look_at_world(x=x, y=y, z=z, duration=1.0)
        
    def run(self):
        """메인 루프"""
        self.speak("음성 제어 모드를 시작합니다.")
        
        try:
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
        finally:
            self.p.terminate()

if __name__ == "__main__":
    controller = ReachyVoiceControl()
    controller.run()
