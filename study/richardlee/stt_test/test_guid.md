# STT 및 VAD 평가 시스템 테스트 가이드 (How to Test)

본 문서는 구축된 STT/VAD 평가 스크립트(`stt_evaluation.py`)를 실행하고, 테스트 케이스를 직접 제어하는 방법에 관한 상세 설명서입니다.

---

## 🚀 1. 터미널(PowerShell)에서 벤치마크 실행하기

### 🅰️ 가장 추천하는 표준 실행법 (루트 폴더 기준)
PowerShell을 실행하고 프로젝트 루트 폴더(`C:\work\richymini`)로 이동한 뒤 가상환경 파이썬을 가리켜 작동시킵니다.

1. **프로젝트 루트 폴더로 이동:**
   ```powershell
   cd C:\work\richymini
   ```
2. **평가 스크립트 구동:**
   ```powershell
   .venv\Scripts\python.exe stt_evaluation.py
   ```

---

### 🅱️ 가상환경 Scripts 폴더에 위치해 있을 때의 실행법
만약 터미널 경로가 `C:\work\richymini\.venv\Scripts`로 고정되어 있고 다른 곳으로 이동하고 싶지 않다면, 부모 디렉토리에 있는 평가 스크립트를 다음과 같이 상대 경로로 지정하여 호출해야 합니다:
```powershell
python.exe ..\..\stt_evaluation.py
```
*(단순히 `python.exe stt_evaluation.py`를 실행할 경우, 파일 위치 불일치로 `No such file or directory` 에러가 발생합니다.)*

---

## 🛠️ 2. 테스트 환경 커스터마이징 방법

### ① 테스트용 오디오 문장 변경/추가하기
[stt_evaluation.py](file:///c:/work/richymini/stt_evaluation.py#L274) 파일 내 `generate_tts_samples` 함수 안의 **`tts_configs`** 리스트를 수정해 주시면 됩니다. 
원하는 문장과 파일명, 언어를 기입하면 다음 실행 시 구글 TTS와 로컬 FFmpeg을 통해 실시간으로 신규 오디오 샘플이 자동 생성 및 인코딩됩니다.

```python
tts_configs = [
    {
        "filename": ".venv/sample_ko_mytest.wav", # 저장할 파일 이름
        "text": "리치 미니 로봇에게 새로운 명령어를 전달합니다.", # 합성할 텍스트 (GT)
        "lang": "ko" # 한국어(ko) 또는 영어(en)
    },
    # 추가하고 싶은 샘플을 여기에 계속 나열할 수 있습니다.
]
```

### ② Whisper 모델 변경하기 (base ↔ tiny)
[stt_evaluation.py](file:///c:/work/richymini/stt_evaluation.py#L416)의 `main()` 함수 초반부에서 불러올 모델 사이즈를 직접 지정할 수 있습니다:

* **base 모델 사용 시 (정확성 극대화 - 기본값 권장)**:
  ```python
  whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
  ```
* **tiny 모델 사용 시 (연산 속도 극대화 - 400ms 미만)**:
  ```python
  whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
  ```

---

## 📓 3. Jupyter Notebook에서 개별 지표 채점하기

작업 중이신 [tts_test.ipynb](file:///c:/work/richymini/.venv/tts_test.ipynb) 내의 새 셀에 아래 코드를 그대로 붙여넣고 실행하면, 오디오 파일 없이도 임의의 두 텍스트 간 정확성을 즉석에서 계산하고 비교 채점할 수 있습니다.

```python
import sys
import os

# 프로젝트 루트 경로 등록 (stt_evaluation 모듈 로딩용)
sys.path.append("C:/work/richymini")
from stt_evaluation import calculate_cer, calculate_wer

# 1. 정답 텍스트와 AI 전사 결과 입력
ground_truth = "안녕하세요 반갑습니다 오늘 날씨가 아주 좋네요"
prediction = "안녕하셔요 반갑습니다 오늘 날씨가 아주 좋내요"

# 2. 메트릭 계산
cer_space = calculate_cer(ground_truth, prediction, ignore_spaces=False)
cer_no_space = calculate_cer(ground_truth, prediction, ignore_spaces=True)
wer = calculate_wer(ground_truth, prediction)

# 3. 결과 출력 (오류율이 낮을수록 정확도가 높은 것입니다)
print(f"Ground Truth (정답) : \"{ground_truth}\"")
print(f"Prediction   (인식) : \"{prediction}\"")
print("-" * 55)
print(f"📊 CER (공백 포함 오류율): {cer_space*100:.1f}%")
print(f"📊 CER (공백 제외 오류율): {cer_no_space*100:.1f}% (정확도: {(1 - cer_no_space)*100:.1f}%)")
print(f"📊 WER (어절 단위 오류율): {wer*100:.1f}%")
```
