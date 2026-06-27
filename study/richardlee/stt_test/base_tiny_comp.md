# Faster-Whisper base vs tiny 모델 비교 보고서 (10개 TTS 샘플 기준)

본 보고서는 16kHz 모노 WAV로 정제된 **10개의 TTS 오디오 샘플(한국어 5개, 영어 5개)**을 대상으로 **`base` 모델**과 **`tiny` 모델**의 지연 시간(VAD, STT) 및 텍스트 정확성(CER/WER)을 비교한 최종 성능 분석 자료입니다.

---

## 📊 1. 종합 성능 비교 요약 (10개 샘플 평균치)

| 평가 모델 | 평균 STT 추론 속도 | 평균 VAD 지연 시간 | 평균 CER (공백 포함) | 평균 CER (공백 제외) | 평균 WER | 종합 평가 |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`base`** | `702.8ms` | `700.0ms` | **`3.8%`** | **`3.6%` (정확도 96.4%)** | `11.5%` | 🟢 정확성 최우수 / 🟡 속도 보통 |
| **`tiny`** | **`391.0ms`** | `700.0ms` | `4.3%` | `4.6%` (정확도 95.4%) | **`10.4%`** | 🟢 속도 우수 / 🟢 정확성 합격 |

> [!NOTE]
> * **속도 비교**: `tiny` 모델이 `base` 모델에 비해 **평균 약 311ms (44.3% 가량) 빨라집니다.**
> * **정확성 비교**: `base` 모델이 공백제외 CER 기준 **`3.6%`**로 `tiny` 모델(`4.6%`)보다 약 1%p 우월합니다. 10개의 고음질 샘플 조건에서는 두 모델 모두 정확도 95% 이상으로 최우수 합격점을 만족했습니다.

---

## 📝 2. 개별 샘플별 인식 결과 세부 비교 (10개 샘플)

### ① sample_ko_weather.wav (한국어 일상)
* **Ground Truth**: `"안녕하세요. 오늘 날씨가 아주 맑고 좋습니다."`
* **모델별 결과**:
  * **`base` 모델**: `"안녕하세요. 오늘 날씨가 아주 맑고 좋습니다."` (CER: **0.0%** / 속도: `660.8ms`)
  * **`tiny` 모델**: `"안녕하세요. 오늘 날씨가 아주 맑고 좋습니다."` (CER: **0.0%** / 속도: `384.3ms`)

### ② sample_ko_robot.wav (한국어 로봇 제어 명령 1)
* **Ground Truth**: `"로봇 팔을 위로 올려주시고 안테나를 움직여 주세요."`
* **모델별 결과**:
  * **`base` 모델**: `"로봇파를 위로 올려주시고 안테나를 움직여 주세요."` (CER(공백X): **9.5%** / 속도: `852.4ms`)
  * **`tiny` 모델**: `"로버팔을 위로 올려주시고 안테날을 움직여 주세요."` (CER(공백X): **14.3%** / 속도: `529.9ms`)
  * *`base` 모델은 단어 왜곡("로봇 팔" ➡️ "로봇파")이 있었으나 조사는 유지했습니다. 반면 `tiny` 모델은 명사 왜곡("로버팔")과 함께 조사가 축약("안테나를" ➡️ "안테날")되었습니다.*

### ③ sample_ko_wing.wav (한국어 로봇 제어 명령 2)
* **Ground Truth**: `"오른쪽 날개를 접고 왼쪽 날개를 활짝 펴주세요."`
* **모델별 결과**:
  * **`base` 모델**: `"오른쪽 날개를 접고 왼쪽 날개를 활짝 펴주세요."` (CER: **0.0%** / 속도: `765.4ms`)
  * **`tiny` 모델**: `"오른쪽 날개를 접고 왼쪽 날개를 활짝 펴주세요."` (CER: **0.0%** / 속도: `381.2ms`)

### ④ sample_ko_move.wav (한국어 로봇 제어 명령 3)
* **Ground Truth**: `"천천히 앞으로 이동하면서 카메라 센서를 켜세요."`
* **모델별 결과**:
  * **`base` 모델**: `"천천히 앞으로 이동하면서 카메라 센서를 켜세요"` (CER: **0.0%** / 속도: `772.4ms`)
  * **`tiny` 모델**: `"천천히 앞으로 이동하면서 카메라 센서를 켜세요."` (CER: **0.0%** / 속도: `372.1ms`)

### ⑤ sample_ko_schedule.wav (한국어 일상 질문)
* **Ground Truth**: `"오늘 스케줄과 읽지 않은 전자 우편을 확인해 줘."`
* **모델별 결과**:
  * **`base` 모델**: `"오늘 스케줄과 익지 않은 전자 우편을 확인해줘"` (CER(공백X): **5.3%** / 속도: `724.0ms`)
  * **`tiny` 모델**: `"오늘 스케줄과 잊지 않은 전자 우편을 확인해 줘."` (CER(공백X): **5.3%** / 속도: `379.3ms`)
  * *`base` 모델은 "읽지 않은"을 "익지 않은"으로, `tiny` 모델은 "잊지 않은"으로 유사 발음 오인식이 각 1글자씩 발생했습니다.*

### ⑥ sample_en_hello.wav (영어 기본 명령)
* **Ground Truth**: `"Please move your head forward and say hello."`
* **모델별 결과**:
  * **`base` 모델**: `"Please move your head forward and say hello."` (CER: **0.0%** / 속도: `638.4ms`)
  * **`tiny` 모델**: `"Please move your head forward and say hello."` (CER: **0.0%** / 속도: `415.0ms`)

### ⑦ sample_en_robot.wav (영어 기술적 서술)
* **Ground Truth**: `"Reachy Mini is a beautiful open source robot."`
* **모델별 결과**:
  * **`base` 모델**: `"Reachie Mini is a beautiful open-source robot."` (CER: **5.4%** / 속도: `637.9ms`)
  * **`tiny` 모델**: `"Richie Mini is a beautiful open-source robot."` (CER: **10.8%** / 속도: `377.6ms`)

### ⑧ sample_en_motor.wav (영어 하드웨어 명령 1)
* **Ground Truth**: `"Turn off the motor controller and disable the antennas."`
* **모델별 결과**:
  * **`base` 모델**: `"Turn off the motor controller and disable the antennas."` (CER: **0.0%** / 속도: `645.4ms`)
  * **`tiny` 모델**: `"Turn off the motor controller and disable the antennas."` (CER: **0.0%** / 속도: `360.9ms`)

### ⑨ sample_en_rotate.wav (영어 하드웨어 명령 2)y_comp
* **Ground Truth**: `"Rotate your body to the right by thirty degrees."`
* **모델별 결과**:
  * **`base` 모델**: `"Rotate your body to the right by 30 degrees."` (CER(공백X): **15.4%** / 속도: `657.4ms`)
  * **`tiny` 모델**: `"Rotate your body to the right by 30 degrees."` (CER(공백X): **15.4%** / 속도: `329.3ms`)
  * *두 모델 모두 영어 단어 "thirty"를 숫자 "30"으로 치환 전사하여 형태소적 오류율이 동률로 집계되었습니다. (실제 음성 전사 품질은 우수함)*

### ⑩ sample_en_name.wav (영어 질문)
* **Ground Truth**: `"What is your name and what can you do for me?"`
* **모델별 결과**:
  * **`base` 모델**: `"What is your name and what can you do for me?"` (CER: **0.0%** / 속도: `674.2ms`)
  * **`tiny` 모델**: `"What is your name and what can you do for me?"` (CER: **0.0%** / 속도: `380.1ms`)

---

## 🔍 결론 및 의사결정 권장사항

1. **지연 시간 대비 정확성 가이드**:
   * 음향 잡음이 없는 스튜디오 수준(gTTS 정제 파일)에서는 **`tiny` 모델**도 CER **4.6%**로 매우 훌륭한 수준을 보여주어, 속도가 생명인 경량 시스템에서 채택하기에 무리가 없습니다.
   * 다만 실생활 마이크 녹음 환경에서는 노이즈가 유입될 수 있으므로, 문맥에 대한 내구성이 강한 **`base` 모델(CER 3.6%)**을 우선 권장합니다.
2. **한국어 어절 오류율(WER) 해석 주의**:
   * 띄어쓰기를 지키지 않으면 오류로 잡히는 WER 특성상, `tiny` 모델의 평균 WER(`10.4%`)이 `base` 모델(`11.5%`)보다 낮게 나오는 수치적 왜곡이 존재합니다. 한국어 평가 시에는 반드시 글자의 개별 정확성을 담보하는 **CER(공백제외)** 지표를 기준 척도로 삼아야 합니다.
