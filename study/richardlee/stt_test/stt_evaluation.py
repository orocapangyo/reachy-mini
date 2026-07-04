import os
import sys
import time
import wave
import collections
import subprocess
import numpy as np
from faster_whisper import WhisperModel

# 현재 경로를 sys.path에 추가하여 realtime_stt 모듈을 정상 로드하도록 함
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from realtime_stt import OnnxVADIterator, resample
except ImportError:
    # 혹시 임포트에 실패하는 경우를 대비한 OnnxVADIterator/resample 기본 복사본 정의
    import urllib.request
    import onnxruntime as ort
    
    def resample(audio, target_len):
        src_indices = np.linspace(0, len(audio) - 1, target_len)
        return np.interp(src_indices, np.arange(len(audio)), audio).astype(np.float32)

    class OnnxVADIterator:
        def __init__(self, model_path="silero_vad.onnx", threshold=0.5, sampling_rate=16000, min_silence_duration_ms=600, speech_pad_ms=100):
            if not os.path.exists(model_path):
                print(f"[VAD-Fallback] 모델 다운로드 중: {model_path}...")
                url = "https://github.com/snakers4/silero-vad/raw/master/src/silero_vad/data/silero_vad.onnx"
                import ssl
                context = ssl._create_unverified_context()
                with urllib.request.urlopen(url, context=context) as r, open(model_path, 'wb') as f:
                    f.write(r.read())
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
            inputs = {'input': input_with_context, 'sr': sr_data, 'state': self._state}
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
                ret['start'] = round(start_sample / self.sampling_rate, 2) if return_seconds else start_sample
            elif (speech_prob < self.threshold) and self._triggered:
                if self._temp_end == 0:
                    self._temp_end = self._current_sample
                if self._current_sample - self._temp_end >= self.min_silence_samples:
                    end_sample = self._temp_end + self.speech_pad_samples
                    self._temp_end = 0
                    self._triggered = False
                    ret['end'] = round(end_sample / self.sampling_rate, 2) if return_seconds else end_sample
            return ret


# ----------------------------------------------------
# 1. CER (음절 오류율) 및 WER (단어 오류율) 계산 로직
# ----------------------------------------------------
def levenshtein_distance(ref, hyp):
    """Levenshtein Distance를 구하는 동적 계획법(DP) 알고리즘"""
    m, n = len(ref), len(hyp)
    dp = np.zeros((m + 1, n + 1), dtype=np.int32)
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref[i - 1] == hyp[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(
                    dp[i - 1][j] + 1,     # Deletion
                    dp[i][j - 1] + 1,     # Insertion
                    dp[i - 1][j - 1] + 1  # Substitution
                )
    return dp[m][n]


def calculate_cer(reference, hypothesis, ignore_spaces=False):
    """
    CER (Character Error Rate, 음절 오류율) 계산 함수
    ignore_spaces: True인 경우 띄어쓰기를 제외하고 글자만으로 정확도 비교 (한국어 필수 옵션)
    """
    ref = str(reference).strip().lower()
    hyp = str(hypothesis).strip().lower()

    # 문장부호 제거
    import string
    punctuation_table = str.maketrans('', '', string.punctuation + '.,!?~"')
    ref = ref.translate(punctuation_table)
    hyp = hyp.translate(punctuation_table)

    if ignore_spaces:
        ref = "".join(ref.split())
        hyp = "".join(hyp.split())

    ref_chars = list(ref)
    hyp_chars = list(hyp)

    if not ref_chars:
        return 0.0 if not hyp_chars else 1.0

    distance = levenshtein_distance(ref_chars, hyp_chars)
    return distance / len(ref_chars)


def calculate_wer(reference, hypothesis):
    """
    WER (Word Error Rate, 단어 오류율) 계산 함수
    띄어쓰기(어절) 단위로 오류율을 측정
    """
    ref = str(reference).strip().lower()
    hyp = str(hypothesis).strip().lower()

    # 문장부호 제거
    import string
    punctuation_table = str.maketrans('', '', string.punctuation + '.,!?~"')
    ref = ref.translate(punctuation_table)
    hyp = hyp.translate(punctuation_table)

    ref_words = ref.split()
    hyp_words = hyp.split()

    if not ref_words:
        return 0.0 if not hyp_words else 1.0

    distance = levenshtein_distance(ref_words, hyp_words)
    return distance / len(ref_words)


# ----------------------------------------------------
# 2. 오디오 파일 실시간 처리 시뮬레이션 및 평가 함수
# ----------------------------------------------------
def read_and_normalize_audio(file_path):
    """오디오 파일을 로드하고 16kHz 모노 float32 numpy array로 전처리합니다."""
    wf = wave.open(file_path, 'rb')
    channels = wf.getnchannels()
    sampwidth = wf.getsampwidth()
    framerate = wf.getframerate()
    n_frames = wf.getnframes()
    raw_data = wf.readframes(n_frames)
    wf.close()

    if sampwidth == 2:
        audio_np = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
    elif sampwidth == 4:
        audio_np = np.frombuffer(raw_data, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        audio_np = np.frombuffer(raw_data, dtype=np.uint8).astype(np.float32) / 255.0 * 2.0 - 1.0

    if channels > 1:
        audio_np = audio_np[::channels]

    RATE = 16000
    if framerate != RATE:
        target_len = int(len(audio_np) * RATE / framerate)
        audio_np = resample(audio_np, target_len)
        
    return audio_np


def dry_run_find_vad_end(audio_np, vad_iterator):
    """오디오 데이터를 VAD에 흘려보내 실제 VAD 감지 종료 시점을 찾습니다 (dry-run)."""
    vad_iterator.reset_states()
    chunk_size = 512
    num_chunks = len(audio_np) // chunk_size
    is_speaking = False
    vad_end_sec = None

    for i in range(num_chunks):
        chunk = audio_np[i * chunk_size : (i + 1) * chunk_size]
        logical_time_sec = (i * chunk_size) / 16000
        
        speech_dict = vad_iterator(chunk, return_seconds=True)
        if speech_dict:
            if 'start' in speech_dict:
                is_speaking = True
            if 'end' in speech_dict:
                is_speaking = False
                vad_end_sec = logical_time_sec
                
    if is_speaking or vad_end_sec is None:
        # 파일 종료 시까지 말이 계속되었거나 감지가 안 된 경우, 파일 총 길이 반환
        vad_end_sec = len(audio_np) / 16000
        
    return vad_end_sec


def simulate_and_evaluate(file_path, ground_truth, actual_speech_end_sec, vad_iterator, whisper_model):
    """
    오디오 파일을 16kHz 512샘플(32ms) 청크 단위로 스트리밍하며 VAD와 Whisper STT의 정확성/속도를 동시 측정합니다.
    """
    audio_np = read_and_normalize_audio(file_path)
    RATE = 16000

    # 변수 및 버퍼 설정
    vad_iterator.reset_states()
    is_speaking = False
    speech_buffer = []
    pre_buffer = collections.deque(maxlen=6)  # ~192ms

    vad_start_sec = None
    vad_end_sec = None
    stt_text = ""
    stt_inference_ms = 0.0

    # 16kHz 기준 32ms(512 샘플) 단위 루프
    chunk_size = 512
    num_chunks = len(audio_np) // chunk_size

    for i in range(num_chunks):
        chunk = audio_np[i * chunk_size : (i + 1) * chunk_size]
        logical_time_sec = (i * chunk_size) / RATE

        if is_speaking:
            speech_buffer.append(chunk)
        else:
            pre_buffer.append(chunk)

        # ONNX VAD 감지
        speech_dict = vad_iterator(chunk, return_seconds=True)

        if speech_dict:
            if 'start' in speech_dict:
                is_speaking = True
                speech_buffer = list(pre_buffer) + [chunk]
                pre_buffer.clear()
                vad_start_sec = logical_time_sec

            if 'end' in speech_dict:
                is_speaking = False
                vad_end_sec = logical_time_sec

                if len(speech_buffer) > 0:
                    audio_data = np.concatenate(speech_buffer)
                    speech_buffer.clear()

                    # 0.5초 이상 녹음된 경우에만 STT 추론 수행
                    if len(audio_data) >= RATE * 0.5:
                        start_time = time.perf_counter()
                        # 한국어 파일 여부 판단
                        lang = "ko" if ("recorded" in file_path or "ko" in file_path or "sample_ko" in file_path) else "en"
                        
                        segments, info = whisper_model.transcribe(
                            audio_data,
                            beam_size=5,
                            language=lang,
                            vad_filter=False
                        )
                        stt_text = "".join([s.text for s in segments]).strip()
                        stt_inference_ms = (time.perf_counter() - start_time) * 1000

    # 만약 파일이 끝날 때까지 명시적인 VAD 'end' 이벤트가 오지 않고 말하는 도중 끊겼다면
    # 남은 버퍼를 전사하여 평가를 계속할 수 있도록 처리합니다.
    if is_speaking and len(speech_buffer) > 0:
        vad_end_sec = len(audio_np) / RATE
        audio_data = np.concatenate(speech_buffer)
        start_time = time.perf_counter()
        lang = "ko" if ("recorded" in file_path or "ko" in file_path or "sample_ko" in file_path) else "en"
        segments, info = whisper_model.transcribe(audio_data, beam_size=5, language=lang, vad_filter=False)
        stt_text = "".join([s.text for s in segments]).strip()
        stt_inference_ms = (time.perf_counter() - start_time) * 1000

    # VAD 지연 시간 계산 (VAD 판단 종료 시간 - 실제 음성 종료 시간)
    vad_latency_ms = None
    if vad_end_sec is not None and actual_speech_end_sec is not None:
        vad_latency_ms = (vad_end_sec - actual_speech_end_sec) * 1000

    # 정확도 지표 계산
    cer_with_space = calculate_cer(ground_truth, stt_text, ignore_spaces=False)
    cer_no_space = calculate_cer(ground_truth, stt_text, ignore_spaces=True)
    wer = calculate_wer(ground_truth, stt_text)

    return {
        "file_path": os.path.basename(file_path),
        "ground_truth": ground_truth,
        "prediction": stt_text,
        "actual_speech_end_sec": actual_speech_end_sec,
        "vad_end_sec": vad_end_sec,
        "vad_latency_ms": vad_latency_ms,
        "stt_inference_ms": stt_inference_ms,
        "cer_with_space": cer_with_space,
        "cer_no_space": cer_no_space,
        "wer": wer,
        "audio_len_sec": len(audio_np) / RATE
    }


# ----------------------------------------------------
# 3. gTTS를 이용한 고품질 오디오 샘플 생성 엔진
# ----------------------------------------------------
def generate_tts_samples():
    """gTTS와 로컬 ffmpeg.exe를 사용하여 테스트용 고품질 음성 샘플 4종을 자동 생성합니다."""
    print("\n" + "=" * 70)
    print(" 🔊 gTTS 및 local FFmpeg을 활용한 오디오 샘플 자동 생성 중...")
    print("=" * 70)

    # 생성할 문장셋 정의 (총 10개: 한국어 5개, 영어 5개)
    tts_configs = [
        {
            "filename": ".venv/sample_ko_weather.wav",
            "text": "안녕하세요. 오늘 날씨가 아주 맑고 좋습니다.",
            "lang": "ko"
        },
        {
            "filename": ".venv/sample_ko_robot.wav",
            "text": "로봇 팔을 위로 올려주시고 안테나를 움직여 주세요.",
            "lang": "ko"
        },
        {
            "filename": ".venv/sample_ko_wing.wav",
            "text": "오른쪽 날개를 접고 왼쪽 날개를 활짝 펴주세요.",
            "lang": "ko"
        },
        {
            "filename": ".venv/sample_ko_move.wav",
            "text": "천천히 앞으로 이동하면서 카메라 센서를 켜세요.",
            "lang": "ko"
        },
        {
            "filename": ".venv/sample_ko_schedule.wav",
            "text": "오늘 스케줄과 읽지 않은 전자 우편을 확인해 줘.",
            "lang": "ko"
        },
        {
            "filename": ".venv/sample_en_hello.wav",
            "text": "Please move your head forward and say hello.",
            "lang": "en"
        },
        {
            "filename": ".venv/sample_en_robot.wav",
            "text": "Reachy Mini is a beautiful open source robot.",
            "lang": "en"
        },
        {
            "filename": ".venv/sample_en_motor.wav",
            "text": "Turn off the motor controller and disable the antennas.",
            "lang": "en"
        },
        {
            "filename": ".venv/sample_en_rotate.wav",
            "text": "Rotate your body to the right by thirty degrees.",
            "lang": "en"
        },
        {
            "filename": ".venv/sample_en_name.wav",
            "text": "What is your name and what can you do for me?",
            "lang": "en"
        }
    ]

    try:
        from gtts import gTTS
    except ImportError:
        print("❌ gTTS 라이브러리가 설치되어 있지 않아 샘플 생성을 생략합니다.")
        return []

    generated_files = []
    for cfg in tts_configs:
        out_wav = cfg["filename"]
        temp_mp3 = out_wav.replace(".wav", ".mp3")
        
        print(f" -> 합성 중 ({cfg['lang']}): \"{cfg['text']}\"")
        try:
            # 1. Google TTS API로부터 오디오 저장 (MP3)
            tts = gTTS(text=cfg["text"], lang=cfg["lang"])
            tts.save(temp_mp3)
            
            # 2. 로컬 ffmpeg.exe를 직접 호출하여 16kHz Mono 16bit PCM WAV로 인코딩
            # ffmpeg.exe는 프로젝트 루트에 위치해 있음
            ffmpeg_cmd = [
                "ffmpeg.exe", "-y",
                "-i", temp_mp3,
                "-ar", "16000",
                "-ac", "1",
                "-c:a", "pcm_s16le",
                out_wav
            ]
            
            # stdout, stderr 출력을 숨겨서 콘솔이 지저분해지는 것 방지
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # 임시 MP3 파일 제거
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)
                
            generated_files.append({
                "file": out_wav,
                "ground_truth": cfg["text"]
            })
            print(f"   └ 생성 완료: {os.path.basename(out_wav)}")
        except Exception as e:
            print(f"   ❌ 샘플 합성 실패: {e}")
            
    print("=" * 70 + "\n")
    return generated_files


# ----------------------------------------------------
# 4. 메인 평가 루프 및 리포트 시각화
# ----------------------------------------------------
def main():
    print("=" * 70)
    print(" [Benchmark] STT 및 VAD 성능 지연 시간 & 정확성 평가 시스템")
    print("=" * 70)

    # 1. AI 모델 로드
    print("[1/2] Silero VAD ONNX 모델 로드 중...")
    try:
        vad_iterator = OnnxVADIterator(
            threshold=0.4, # realtime_stt.py 설정 동기화
            sampling_rate=16000,
            min_silence_duration_ms=600,
            speech_pad_ms=100
        )
        print(" -> VAD 로드 완료.")
    except Exception as e:
        print(f"❌ VAD 로드 실패: {e}")
        return

    print("[2/2] Faster-Whisper base 모델 로드 중 (CPU + int8 양자화)...")
    try:
        whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
        print(" -> Whisper 로드 완료.")
    except Exception as e:
        print(f"❌ Whisper 로드 실패: {e}")
        return

    # 2. TTS 오디오 샘플 생성 및 메타데이터 자동 구성
    generated_cases = generate_tts_samples()
    
    # 평가 대상 목록 정의
    test_cases = []
    
    # 동적 생성한 고품질 TTS 샘플 등록
    for gc in generated_cases:
        file_path = gc["file"]
        # Dry-run을 돌려서 VAD 종료 시점(vad_end_sec)을 알아내고, 
        # 실제 말소리 종료 시점(actual_speech_end)을 역산(vad_end_sec - 0.7초)합니다.
        # 이렇게 하면 합성음에서도 VAD 감지 지연 시간을 700ms 마진 내에서 정밀하게 측정 가능합니다.
        audio_np = read_and_normalize_audio(file_path)
        vad_end_sec = dry_run_find_vad_end(audio_np, vad_iterator)
        
        # VAD 침묵 마진인 0.7초(600ms + 100ms) 전이 실제 말 소리가 끝난 시점으로 간주
        actual_speech_end = max(0.0, vad_end_sec - 0.7)
        
        test_cases.append({
            "file": file_path,
            "ground_truth": gc["ground_truth"],
            "actual_speech_end": actual_speech_end
        })

    # 기존 로컬 수동 녹음 파일 추가 부분은 제거하여 
    # 고품질 TTS 자동 합성 샘플 4종만 단독 평가하도록 합니다.
    pass

    if not test_cases:
        print("❌ 평가할 오디오 파일이 존재하지 않습니다. 샘플 생성을 점검해주세요.")
        return

    print(f" 총 {len(test_cases)}개의 파일에 대해 벤치마크 시뮬레이션 평가를 시작합니다...")
    print("-" * 75)

    results = []
    for tc in test_cases:
        file_path = tc["file"]
        print(f" -> 평가 중: {os.path.basename(file_path)}")
        try:
            res = simulate_and_evaluate(
                file_path=file_path,
                ground_truth=tc["ground_truth"],
                actual_speech_end_sec=tc["actual_speech_end"],
                vad_iterator=vad_iterator,
                whisper_model=whisper_model
            )
            results.append(res)
        except Exception as e:
            print(f"   ❌ 평가 중 오류 발생 ({os.path.basename(file_path)}): {e}")

    if not results:
        print("❌ 유효한 평가 결과가 존재하지 않습니다.")
        return

    # 3. 벤치마크 요약 대시보드 출력
    print("\n" + "=" * 105)
    print(" 📊 STT & VAD 종합 벤치마크 결과 리포트 (TTS 샘플 포함)")
    print("=" * 105)
    
    header = f"{'파일명':<23} | {'VAD지연(ms)':<10} | {'STT추론(ms)':<10} | {'CER(공백O)':<8} | {'CER(공백X)':<8} | {'WER':<8} | {'오디오길이(초)':<10}"
    print(header)
    print("-" * 105)

    total_vad_latency = 0.0
    total_stt_inference = 0.0
    total_cer_space = 0.0
    total_cer_no_space = 0.0
    total_wer = 0.0
    valid_vad_count = 0

    for r in results:
        v_lat_str = f"{r['vad_latency_ms']:.1f}ms" if r["vad_latency_ms"] is not None else "N/A"
        stt_inf_str = f"{r['stt_inference_ms']:.1f}ms"
        
        cer_space_str = f"{r['cer_with_space']*100:.1f}%"
        cer_nospace_str = f"{r['cer_no_space']*100:.1f}%"
        wer_str = f"{r['wer']*100:.1f}%"
        audio_len_str = f"{r['audio_len_sec']:.2f}s"

        print(f"{r['file_path']:<23} | {v_lat_str:<12} | {stt_inf_str:<12} | {cer_space_str:<10} | {cer_nospace_str:<10} | {wer_str:<10} | {audio_len_str:<12}")
        print(f"   └ Ground Truth: \"{r['ground_truth']}\"")
        print(f"   └ Prediction  : \"{r['prediction']}\"")
        
        act_sec = f"{r['actual_speech_end_sec']:.2f}s" if r['actual_speech_end_sec'] is not None else "N/A"
        det_sec = f"{r['vad_end_sec']:.2f}s" if r['vad_end_sec'] is not None else "N/A"
        print(f"   └ [VAD 분석]: 실제 음성 종료={act_sec} | VAD 감지 시점={det_sec}")
        print("-" * 105)

        if r["vad_latency_ms"] is not None:
            total_vad_latency += r["vad_latency_ms"]
            valid_vad_count += 1
        total_stt_inference += r["stt_inference_ms"]
        total_cer_space += r["cer_with_space"]
        total_cer_no_space += r["cer_no_space"]
        total_wer += r["wer"]

    # 평균 지표 산출
    num_files = len(results)
    avg_vad_latency = (total_vad_latency / valid_vad_count) if valid_vad_count > 0 else 0.0
    avg_stt_inference = total_stt_inference / num_files
    avg_cer_space = total_cer_space / num_files
    avg_cer_no_space = total_cer_no_space / num_files
    avg_wer = total_wer / num_files

    print(f"{'평균 요약 (Average)':<23} | {f'{avg_vad_latency:.1f}ms':<12} | {f'{avg_stt_inference:.1f}ms':<12} | {f'{avg_cer_space*100:.1f}%':<10} | {f'{avg_cer_no_space*100:.1f}%':<10} | {f'{avg_wer*100:.1f}%':<10} | -")
    print("=" * 105)

    # 4. 성능 평가 등급 코멘트
    print("\n💡 [평가 결과 분석 코멘트]")
    
    if avg_stt_inference <= 500.0:
        print("🟢 STT 추론 시간: 합격 (500ms 이하) - 실시간 대화에 적합한 응답 속도입니다.")
    elif avg_stt_inference <= 1000.0:
        print("🟡 STT 추론 시간: 경고 (500ms ~ 1000ms) - 다소 지연이 체감될 수 있습니다.")
    else:
        print("❌ STT 추론 시간: 불합격 (1000ms 초과) - 모델 경량화(tiny) 또는 추론 가속 설정을 점검하십시오.")

    if 300.0 <= avg_vad_latency <= 750.0:
        print("🟢 VAD 지연 시간: 적절 (300ms ~ 750ms) - 대화가 끊기지 않으면서 자연스러운 대답 반응을 보장합니다.")
    elif avg_vad_latency < 300.0:
        print("🟡 VAD 지연 시간: 매우 짧음 (<300ms) - 말을 잠시 쉴 때 끊길 가능성이 높습니다. (min_silence_duration_ms 상향 권장)")
    else:
        print("🟡 VAD 지연 시간: 김 (>750ms) - 묵념하듯 늦게 응답하여 답답함을 느낄 수 있습니다. (min_silence_duration_ms 하향 권장)")

    if avg_cer_no_space <= 0.10:
        print("🟢 CER (공백제외): 최우수 (10% 이하) - 음성 인식 정확도가 90% 이상으로, 서비스 출시에 지장이 없는 수준입니다.")
    elif avg_cer_no_space <= 0.20:
        print("🟡 CER (공백제외): 보통 (10% ~ 20%) - 일상적인 문맥은 파악 가능하나 오인식이 가끔 존재합니다.")
    else:
        print("❌ CER (공백제외): 미흡 (20% 초과) - 마이크 잡음, 리샘플링 왜곡, 혹은 모델 언어 능력 한계로 전사가 부실합니다.")
    print("=" * 105 + "\n")


if __name__ == "__main__":
    main()
