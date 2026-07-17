### ⚖️ 오디오 아키텍처 비교 요약

| 비교 항목 | 🔄 비동기 인프로세스 방식 (Async In-Process) | 🌐 서버-클라이언트 방식 (Server-Client) |
| :--- | :--- | :--- |
| **개념** | 하나의 파이썬 앱(`asyncio` 등) 안에서 로봇 제어와 STT/TTS 모델을 한 번에 실행 | 로봇 제어(앱)와 STT/TTS/LLM(서버)을 별도의 프로세스로 분리하여 웹소켓 연동 |
| **연산 및 자원 관리** | 파이썬의 GIL(전역 인터프리터 락) 제약으로 인해 CPU 집약적인 딥러닝 연산 시 로봇 제어 루프가 일시정지(렉)될 수 있음 | 프로세스 격리를 통해 로봇 제어는 저사양 코어에서, 딥러닝은 강력한 GPU 코어에서 각각 독립적으로 실행됨 |
| **안정성 (Crash)** | STT/TTS(PyTorch)에서 OOM(메모리 부족)이나 치명적 오류 발생 시 **로봇 제어 프로그램까지 통째로 꺼짐** | S2S 서버가 죽어도 로봇 앱은 안전 자세로 복귀하는 등의 예외 처리가 가능하여 물리적 사고 방지 |
| **확장성** | 로봇 내부 컴퓨터 사양에 100% 의존해야 함 | 로봇 내부 컴퓨터는 최소 제어만 하고, AI 연산 서버는 성능 좋은 다른 PC나 클라우드로 자유롭게 이전 가능 |
| **지연 시간 (Latency)** | 프로세스 내부 메모리 참조이므로 통신 지연 0ms | 네트워크 직렬화(오디오 바이트 인코딩) 및 웹소켓 통신으로 인해 **약 5~30ms의 지연 추가** |

---

### 1. 비동기 인프로세스(Async) 방식이 유리한 경우
* **순수 소프트웨어 서비스일 때**: 물리 로봇 제어 없이, PC나 스마트폰 화면 속 캐릭터와 대화하는 서비스라면 이 방식이 네트워크 지연(Latency)이 가장 짧기 때문에 반응 속도 면에서 미세하게 유리할 수 있습니다.
* **단순한 토이 프로젝트**: 단 하나의 파이썬 파일만 실행하면 되므로 배포와 세팅이 매우 단순합니다.

---

### 2. 서버-클라이언트(Server) 방식이 유리한 경우 (현재 구조)
* **물리 하드웨어(로봇) 제어가 포함될 때**: 
  로봇의 모터 제어 명령은 1/100초(10ms) 단위의 매우 정밀한 실시간성(Real-time)이 필요합니다. 만약 딥러닝 연산이 프로세스를 선점하여 로봇 제어 명령이 단 0.5초만 밀려도 **로봇 관절이 부자연스럽게 꺾이거나 모터 과열이 발생하는 등의 물리적 위험**이 따릅니다. 
* **분산 처리가 필요할 때**:
  로봇 내부의 초소형 컴퓨터(예: Raspberry Pi)에 무거운 딥러닝 모델들을 얹어서 돌리는 것은 불가능에 가깝습니다. 이를 분리하여 **고사양 그래픽카드가 달린 외부 데스크톱 PC**로 연산을 넘길 수 있는 유일한 대안이 서버 방식입니다.



### 💻 로컬 구동 vs ☁️ 원격/배포 구동 비교

| 구분 | 💻 로컬 구동 (Local Mode) | ☁️ 원격/배포 구동 (Deployed Mode) |
| :--- | :--- | :--- |
| **PC 역할** | **서버**와 **클라이언트** 역할을 모두 수행 | 오직 **클라이언트** 역할만 수행 |
| **백엔드 서버 위치** | 질문자님의 로컬 PC (Ollama, Whisper 등 구동) | 외부 Hugging Face 클라우드 서버 |
| **실행할 명령어** | 1. **(백엔드)** `speech-to-speech ...` CLI 실행<br/>2. **(앱)** `reachy-mini-conversation-app` 실행 | 1. **(백엔드)** 실행 필요 없음 (이미 배포됨)<br/>2. **(앱)** `reachy-mini-conversation-app`만 실행 |
| **PC 권장 사양** | 딥러닝 구동을 위한 고사양 GPU 필요 | 기본 CPU 환경에서도 가볍게 실행 가능 |
| **네트워크 상태** | 인터넷이 끊겨도 로컬에서 작동 가능 | 외부 클라우드 접속을 위해 인터넷 연결 필수 |

---
## **S2S WebSocket 서버를 구동**
### 1. 실행하실 방법 (Kokoro 구동)
1. **백엔드 서버 터미널**에서 다시 `kokoro` 옵션으로 서버를 켭니다:
   ```powershell
   speech-to-speech --llm_backend responses-api --responses_api_base_url http://localhost:11434/v1 --model_name gemma4:cloud --responses_api_api_key dummy --device cpu --tts kokoro
   ```
kokoro 한국어 미지원 따라서 다음과 같이 수정

### 2. 1번 옵션이 반응을 안 해 다른 옵션 선택
speech-to-speech --llm_backend responses-api --responses_api_base_url http://localhost:11434/v1 --model_name gemma4:cloud --responses_api_api_key dummy --device cpu --stt whisper --stt_model_name openai/whisper-base --stt_torch_dtype float32 --language ko --tts facebookMMS --tts_language ko

로컬에서 **실시간 S2S WebSocket 서버를 구동(호스팅)하는 명령**.

`speech-to-speech` 패키지가 올바르게 가상환경에 설치(`pip install -e .`)되면 터미널에서 `speech-to-speech`라는 CLI 명령어를 직접 사용할 수 있게 등록됩니다.

### 🔍 실행 명령어 구성 분석

```bash
speech-to-speech \
  --llm_backend responses-api \
  --responses_api_base_url http://localhost:11434/v1 \
  --model_name gemma4:cloud \
  --responses_api_api_key dummy \
  --device cpu \
  --stt whisper \
  --stt_model_name openai/whisper-base \
  --stt_torch_dtype float32 \
  --language ko \
  --tts facebookMMS \
  --tts_language ko
```

* **`--llm_backend responses-api`**: LLM 엔진으로 OpenAI와 호환되는 API 서버(이 경우 로컬 Ollama 등)를 사용하겠다고 지정합니다.
* **`--responses_api_base_url http://localhost:11434/v1`**: Ollama가 로컬 컴퓨터(`localhost:11434`)에서 대기 중인 주소를 설정합니다.
* **`--model_name gemma4:cloud`**: Ollama에 등록된 모델 중 `gemma4:cloud` 모델을 대화 엔진으로 지정합니다.
* **`--device cpu`**: 그래픽 카드(GPU) 대신 **CPU를 사용**하여 로컬에서 STT/TTS 모델 연산을 처리합니다.
* **`--stt whisper --stt_model_name openai/whisper-base`**: 로컬에서 `openai/whisper-base` 모델을 돌려 실시간 음성 인식을 수행합니다.
* **`--stt_torch_dtype float32`**: CPU 실행을 위해 데이터 타입을 `float32`로 지정합니다.
* **`--language ko`**: 대화 언어를 **한국어**로 지정합니다.
* **`--tts facebookMMS --tts_language ko`**: 답변 음성 합성으로 Facebook MMS 한국어 모델을 로컬에서 작동시킵니다.

### 3. 실행 결과 및 연동
이 명령어를 실행하면, 기본적으로 **`ws://localhost:8765`** 주소로 WebSocket 서버가 개설되어 클라이언트의 실시간 음성 스트림 접속을 대기하게 됩니다.

이후 Reachy Mini App의 `.env` 환경 변수를 다음과 같이 연동하여 작동시킵니다.
```env
HF_REALTIME_CONNECTION_MODE=local
HF_REALTIME_WS_URL=ws://localhost:8765/v1/realtime
```



```mermaid

graph TD
    %% 1단계: 사용자 인터랙션 시작
    User["사용자"]

    %% Conversation App 영역
    subgraph App["[Conversation App]"]
        RecLoop["LocalStream.record_loop<br/>(마이크 데이터 캡처)"]
        Handler["HuggingFaceRealtimeHandler<br/>(WebSocket 클라이언트)"]
        BTM["BackgroundToolManager<br/>(도구 실행 관리)"]
        DanceTool["Dance Tool (dance.py)<br/>춤 모션 파일 로드"]
        MoveMgr["MovementManager<br/>(동작 명령 조율)"]
    end

    %% S2S Backend 영역
    subgraph S2S["[Speech to Speech Backend]"]
        STT["STT (Whisper)<br/>음성 ➔ '춤춰' 텍스트 변환"]
        LLM["LLM (Llama / Gemma)<br/>의도 파악 및 도구 호출 결정"]
        TTS["TTS (Facebook MMS)<br/>답변 텍스트 ➔ 음성 합성"]
    end

    %% Reachy Mini SDK 영역
    subgraph SDK["[Reachy Mini SDK / HW]"]
        Mic["Media SDK (마이크 입력)"]
        Daemon["reachy-mini-daemon (제어 데몬)"]
        Motor["로봇 모터 구동"]
        Spk["Media SDK (스피커 출력)"]
    end

    %% 흐름 연결 (리스트 형태 오인을 막기 위해 온점 제외)
    User -->|1단계 음성 발화 춤춰| Mic
    Mic -->|2단계 프레임 캡처| RecLoop
    RecLoop -->|3단계 오디오 스트림 전달| Handler
    Handler -->|4단계 WebSocket 전송| STT
    STT -->|5단계 텍스트 토큰| LLM
    LLM -->|6단계 Tool Call 이벤트 생성| Handler
    Handler -->|7단계 백그라운드 실행 요청| BTM
    BTM -->|8단계 Dance 동작 실행| DanceTool
    DanceTool -->|9단계 DanceQueueMove 궤적 큐잉| MoveMgr
    MoveMgr -->|10단계 모션 패킷 전달| Daemon
    Daemon -->|11단계 서보 모터 동작| Motor
    Motor -->|12단계 댄스 수행 관찰| User

    %% TTS 응답 흐름 추가
    LLM -->|13단계 답변 텍스트| TTS
    TTS -->|14단계 합성된 오디오 스트림| Handler
    Handler -->|15단계 오디오 재생 큐 주입| Spk
    Spk -->|16단계 음성 답변 스피커 출력| User
```
