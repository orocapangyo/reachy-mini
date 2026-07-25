import os
import time
import queue
import threading
import pyaudio
import collections
import urllib.request
import numpy as np
import onnxruntime as ort
from concurrent.futures import ThreadPoolExecutor
from faster_whisper import WhisperModel

# ----------------------------------------------------
# 1. 글로벌 설정 및 파라미터 정의
# ----------------------------------------------------
FORMAT = pyaudio.paInt16       # 16-bit PCM 포맷
CHANNELS = 1                  # 모노 채널
RECORD_RATE = 44100           # 녹음용 샘플링 레이트 (Windows 기본 마이크 표준)
RATE = 16000                  # VAD & Whisper 표준 샘플링 레이트 (16kHz)
TARGET_CHUNK_SIZE = 512       # VAD 입력 크기 (16kHz 기준 32ms)
# 44100Hz에서 32ms에 해당하는 샘플 수 = 44100 * (512 / 16000) = 1411.2 -> 1411
RECORD_CHUNK_SIZE = 1411      

# VAD 감도 및 안전성 설정 (Safety Bounds)
VAD_THRESHOLD = 0.4           # 목소리 감지 임계값 (0.0 ~ 1.0)
MIN_SILENCE_MS = 500          # 🛡️ 침묵 감지 타임아웃 (400ms ~ 600ms 사이 권장, 여기서는 500ms 적용)
SPEECH_PAD_MS = 100           # 시작과 끝 부분의 오디오 패딩(ms)

MAX_DURATION_SECONDS = 20.0   # 🛡️ 최대 녹음 제한 시간 (사용자가 계속 말할 때 강제 커트)
MIN_DURATION_SECONDS = 0.3    # 🛡️ 최소 음성 길이 제한 (노이즈 및 기침 소리 폐기)


def resample(audio, target_len):
    """numpy 선형 보간을 활용한 빠르고 왜곡 없는 다운샘플링"""
    src_indices = np.linspace(0, len(audio) - 1, target_len)
    return np.interp(src_indices, np.arange(len(audio)), audio).astype(np.float32)


def normalize_audio(audio_data, target_peak=0.5, max_gain=5.0):
    """
    🎛️ 오디오 데이터 정규화 (Normalization)
    마이크와의 거리가 멀어 음량이 작은 경우를 보정하기 위해 오디오 진폭을 체크하고 부스팅합니다.
    디지털 노이즈 증폭을 방지하기 위해 최대 증폭 비율(max_gain)을 제한합니다.
    """
    peak = np.max(np.abs(audio_data))
    if peak > 0:
        gain = target_peak / peak
        gain = min(gain, max_gain)  # 노이즈 극단 증폭 방지용 상한선
        if gain > 1.0:
            audio_data = audio_data * gain
            print(f"\n[Preprocessing] 🎛️ 오디오 부스팅 적용: {gain:.2f}x (Peak: {peak:.4f} -> {np.max(np.abs(audio_data)):.4f})")
    return audio_data


# ----------------------------------------------------
# 2. PyTorch/TorchAudio 의존성이 없는 순수 ONNX VAD 클래스 정의
# ----------------------------------------------------
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


# ----------------------------------------------------
# 3. 🧵 멀티스레딩 기반 비차단형(Non-blocking) STT 파이프라인
# ----------------------------------------------------
class NonBlockingSTTPipeline:
    def __init__(self):
        # 3.1 VAD ONNX 모델 로드
        print("[1/2] Silero VAD ONNX 모델 로드 중...")
        self.vad_iterator = OnnxVADIterator(
            threshold=VAD_THRESHOLD,
            sampling_rate=RATE,
            min_silence_duration_ms=MIN_SILENCE_MS,
            speech_pad_ms=SPEECH_PAD_MS
        )
        print(" -> Silero VAD 모델 로드 완료.")

        # 3.2 Faster-Whisper 로드 (⚡ CPU + int8 양자화 적용)
        print("[2/2] Faster-Whisper 모델 로드 중 (CPU + int8 양자화)...")
        self.whisper_model = WhisperModel(
            model_size_or_path="tiny",  # 속도 확보를 위해 'tiny' 혹은 'base' 사용 권장
            device="cpu", 
            compute_type="int8"
        )
        print(" -> Faster-Whisper 모델 로드 완료.")

        self.p = pyaudio.PyAudio()
        
        # 스레드 간 비차단 통신을 위한 Queue 구조
        self.audio_task_queue = queue.Queue()
        self.transcribed_text_queue = queue.Queue()
        
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.is_running = False
        self.recording_thread = None

    def start(self):
        """음성 캡처 및 Whisper 추론 백그라운드 스레드 시작"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # 1) 오디오 녹음 및 VAD 감지를 담당하는 백그라운드 스레드
        self.recording_thread = threading.Thread(target=self._audio_recording_loop, daemon=True)
        self.recording_thread.start()
        
        # 2) 오디오 큐를 모니터링하여 Whisper 추론을 비동기로 돌리는 백그라운드 스레드
        self.inference_thread = threading.Thread(target=self._whisper_inference_loop, daemon=True)
        self.inference_thread.start()
        
        print("\n" + "=" * 60)
        print(" 🎤 백그라운드 넌블로킹 STT 파이프라인 가동 완료!")
        print("=" * 60 + "\n")

    def stop(self):
        """시스템 종료 및 리소스 해제"""
        self.is_running = False
        self.p.terminate()
        self.executor.shutdown(wait=False)
        print("[System] STT 파이프라인이 정지되고 리소스가 정리되었습니다.")

    def _audio_recording_loop(self):
        """마이크 데이터를 캡처하고 VAD로 음성 구간을 분리하여 큐로 전달하는 스레드"""
        try:
            stream = self.p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RECORD_RATE,
                input=True,
                frames_per_buffer=RECORD_CHUNK_SIZE
            )
        except Exception as e:
            print(f"❌ 마이크 스트림 열기 실패: {e}")
            self.is_running = False
            return

        self.vad_iterator.reset_states()
        is_speaking = False
        speech_buffer = []
        pre_buffer = collections.deque(maxlen=6)
        
        max_speech_chunks = int((RATE * MAX_DURATION_SECONDS) / TARGET_CHUNK_SIZE)

        try:
            while self.is_running:
                raw_data = stream.read(RECORD_CHUNK_SIZE, exception_on_overflow=False)
                audio_chunk_np_441 = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
                audio_chunk_np = resample(audio_chunk_np_441, TARGET_CHUNK_SIZE)
                
                if is_speaking:
                    speech_buffer.append(audio_chunk_np)
                    # 🛡️ 안전장치 1: 최대 녹음 시간(MAX_DURATION_SECONDS) 초과 시 강제 컷오프
                    if len(speech_buffer) >= max_speech_chunks:
                        print(f"\n[Safety Bounds] 🛡️ 최대 발화 시간({MAX_DURATION_SECONDS}초) 초과로 강제 컷오프합니다.")
                        is_speaking = False
                        
                        audio_data = np.concatenate(speech_buffer)
                        speech_buffer.clear()
                        self._process_detected_speech(audio_data)
                else:
                    pre_buffer.append(audio_chunk_np)
                
                speech_dict = self.vad_iterator(audio_chunk_np, return_seconds=True)
                
                if speech_dict:
                    if 'start' in speech_dict and not is_speaking:
                        is_speaking = True
                        speech_buffer = list(pre_buffer) + [audio_chunk_np]
                        pre_buffer.clear()
                        print("\n[VAD] 🗣️ 말하기 시작 감지...", end="", flush=True)
                    
                    if 'end' in speech_dict and is_speaking:
                        is_speaking = False
                        print("\n[VAD] 🔇 말하기 종료 감지.", flush=True)
                        
                        if len(speech_buffer) > 0:
                            audio_data = np.concatenate(speech_buffer)
                            speech_buffer.clear()
                            self._process_detected_speech(audio_data)
                            
        except Exception as e:
            print(f"\n[Error] 오디오 캡처 루프 에러: {e}")
        finally:
            stream.stop_stream()
            stream.close()

    def _process_detected_speech(self, audio_data):
        """VAD 종료 후 최소 음성 길이를 검증하고, 정규화 후 Whisper 추론 큐에 적재"""
        audio_duration = len(audio_data) / RATE
        
        # 🛡️ 안전장치 2: 최소 음성 길이 미만의 짧은 신호(노이즈, 기침 등) 폐기
        if audio_duration < MIN_DURATION_SECONDS:
            print(f"[Safety Bounds] 🛡️ 음성 길이 부족({audio_duration:.2f}초 < 최소 {MIN_DURATION_SECONDS}초)으로 오디오를 무시합니다.")
            return

        # 🎛️ 오디오 데이터 정규화 적용
        normalized_audio = normalize_audio(audio_data)
        
        # 비동기 Whisper 스레드로 전송하기 위해 큐에 적재
        self.audio_task_queue.put((normalized_audio, audio_duration))

    def _whisper_inference_loop(self):
        """배경에서 큐를 폴링하여 CPU 최적화 옵션으로 Whisper STT 추론 수행"""
        while self.is_running:
            try:
                audio_data, duration = self.audio_task_queue.get(timeout=0.5)
            except queue.Empty:
                continue
                
            try:
                start_time = time.perf_counter()
                
                # ⚡ Faster-Whisper 최적화 설정 파라미터 적용
                segments, info = self.whisper_model.transcribe(
                    audio_data,
                    beam_size=1,                         # ⚡ 빔 사이즈=1로 극단적 속도 최적화
                    language="ko",                        # ⚡ 언어를 한국어로 강제 고정
                    condition_on_previous_text=False,     # ⚡ 이전 텍스트 문맥 배제로 무한반복 환각 차단
                    vad_filter=False                      # 앞단에서 Silero VAD 완료 상태이므로 False
                )
                
                text = "".join([segment.text for segment in segments]).strip()
                inference_time_ms = (time.perf_counter() - start_time) * 1000
                
                # 결과 큐 전달
                self.transcribed_text_queue.put({
                    "text": text,
                    "duration": duration,
                    "inference_time_ms": inference_time_ms,
                    "language": info.language,
                    "prob": info.language_probability
                })
                
            except Exception as e:
                print(f"\n[Error] Whisper 받아쓰기 에러: {e}")
            finally:
                self.audio_task_queue.task_done()


# ----------------------------------------------------
# 4. 검증 및 구동 시나리오 (메인 루프 차단 없음 확인용)
# ----------------------------------------------------
if __name__ == "__main__":
    # 파이프라인 인스턴스 생성 및 스레드 가동
    pipeline = NonBlockingSTTPipeline()
    pipeline.start()
    
    print("[Main Loop] 로봇 제어 / 통신 데몬 가동 중...")
    print("[Main Loop] Whisper 연산(STT)이 백그라운드에서 실행되는 동안 이 메인 루프는 절대 멈추지 않습니다.")
    
    try:
        loop_count = 0
        while True:
            loop_count += 1
            if loop_count % 2 == 0:
                print(".", end="", flush=True)  # 메인 루프 헬스 체크용 하트비트 출력
                
            # 비차단(Non-blocking) 방식으로 Whisper 변환 결과가 도착했는지 상시 체크
            try:
                result = pipeline.transcribed_text_queue.get_nowait()
                print("\n" + "-" * 50)
                if result["text"]:
                    print(f"👉 [인식 결과]: {result['text']}")
                    print(f"   [성능 측정]: 발화 길이={result['duration']:.2f}초 | STT 소요={result['inference_time_ms']:.1f}ms")
                else:
                    print("👉 [인식 결과]: (음성이 감지되었으나 변환된 문장이 없습니다.)")
                print("-" * 50)
            except queue.Empty:
                pass
                
            time.sleep(0.25)
            
    except KeyboardInterrupt:
        print("\n[System] Ctrl+C 수신. 시스템을 종료합니다.")
    finally:
        pipeline.stop()
```
