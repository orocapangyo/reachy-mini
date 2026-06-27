---
title: Reachy Mini 서브모듈 업데이트
subtitle: 2025 - 2026 주요 변경 사항 정리
badge: 기술 학습 자료
desc: 하드웨어 구성 · 기구 설계 · 미디어 백엔드 · 멀티 OS 지원의 1년간 변화
author: "로버트@오로카판교 (https://arduino-uno-club.lovable.app/)"
header: Reachy Mini Updates (2025 - 2026)
toc: true
toc_depth: 3
---

이 문서는 최근 1년(2025년 6월 ~ 2026년 6월) 동안 [reachy_mini](https://github.com/orocapangyo/reachy-mini) 서브모듈에 적용된 주요 변경 사항과, 그 변경을 이해하는 데 바탕이 되는 **하드웨어 구성·기구 설계**를 함께 정리한 학습 자료입니다. 소프트웨어 변경 내역뿐 아니라, 서브모듈에 공개된 기구 모델(URDF/MJCF)·부품 사양·전장 구성까지 포함해 "무엇이 바뀌었는가"와 "어떤 하드웨어 위에서 동작하는가"를 한 번에 파악하도록 구성했습니다.

---

## 🎤 상세 기술 분석

### 0. 도입부: 1년간의 변화 요약

최근 1년 동안 Reachy Mini 오픈소스 프로젝트는 단순 기능 추가를 넘어 **하드웨어 제어 안정성 확보, 오디오 스트리밍 레이텐시(지연 시간) 최소화, 그리고 다양한 OS 플랫폼(특히 Windows)으로의 확장**이라는 세 가지 중점 과제를 해결해 왔습니다.

이 기간 동안 [.gitmodules](https://github.com/orocapangyo/reachy-mini) 내의 서브모듈을 포함하여 데몬, 미디어 백엔드, 앱 가상환경 전반에 걸쳐 수많은 개선이 이루어졌습니다. 본문에서는 먼저 로봇의 **하드웨어 구성과 기구(메커니즘) 설계**를 짚은 뒤, 그 위에서 동작하는 소프트웨어 변경 사항을 ① 미디어 백엔드, ② 하드웨어/모터 제어, ③ 멀티 OS·개발 도구의 세 축으로 나누어 분석합니다.

> [!NOTE]
> Reachy Mini는 **오픈소스 하드웨어**를 지향합니다. 기구 형상(STL 메시 + URDF/MJCF), 부품 사양(모터·배터리·센서 모델명), 자유도/치수, 기구학 알고리즘, 조립 가이드가 모두 서브모듈 또는 공식 문서로 공개되어 있습니다.

---

### 1. 하드웨어 구성 및 기구(메커니즘) 설계
> **관련 자료**: [docs/.../hardware.md](https://github.com/orocapangyo/reachy-mini) · 기구 모델 [src/reachy_mini/descriptions](https://github.com/orocapangyo/reachy-mini) · 기구학 [src/reachy_mini/kinematics](https://github.com/orocapangyo/reachy-mini)

Reachy Mini는 작은 데스크톱 크기 안에 **6자유도 병렬 메커니즘(스튜어트 플랫폼)** 으로 움직이는 머리, 회전하는 몸통, 표정을 담당하는 안테나 2개를 집약한 표현형(expressive) 로봇입니다.

#### ① 외형 및 전체 사양

| 항목 | Reachy Mini (Wireless) | Reachy Mini Lite |
| :--- | :--- | :--- |
| 크기(확장 시) | 30 × 20 × 15.5 cm | 30 × 20 × 15.5 cm |
| 질량 | 1.475 kg | 1.350 kg |
| 재질 | ABS · PC · 알루미늄 · 스틸 | ABS · PC · 알루미늄 · 스틸 |
| 제어 본체 | Raspberry Pi CM4 (자체 연산, 무선) | USB-C로 외부 PC에 연결 |
| 전원 입력 | 6.8 – 7.6 V | 6.8 – 7.6 V |
| 내장 배터리 | LiFePO4 2000mAh / 6.4V / 12.8Wh | 없음(PC 연결형) |

> 두 모델 모두 기구·모터·센서 구성은 동일하며, **연산 주체(온보드 CM4 vs 외부 PC)와 전원(배터리 내장 여부)** 에서 갈립니다. Lite는 컴퓨터에 꽂아 쓰는 주변기기에 가깝고, Wireless는 자체 연산·배터리로 독립 구동합니다.

#### ② 자유도(DOF) 구성 — 총 9 자유도

* **머리: 6 DOF** — 3축 회전(roll/pitch/yaw) + 3축 병진(x/y/z). 즉 머리가 끄덕임·기울임·돌림은 물론 앞뒤·좌우·상하로 살짝 이동까지 가능합니다.
* **몸통: 1 DOF** — 수직축(yaw) 회전. 머리 6 DOF와 결합해 더 넓은 시선 범위를 만듭니다.
* **안테나: 2 DOF** — 좌/우 각 1축 회전. 동작 자체보다 **감정·상태 표현**용 액추에이터입니다.

#### ③ 머리 메커니즘: 스튜어트 플랫폼(6-DOF 병렬 로봇)

머리는 **6개의 선형 링크(로드+볼조인트)** 가 상·하 플레이트를 연결하는 전형적인 스튜어트 플랫폼(Hexapod) 구조입니다.

* **구조**: 하단 베이스 플레이트에 고정된 6개 모터가 각자의 암(arm)을 회전시키고, 그 끝에 연결된 로드(rod)가 볼조인트를 통해 상단 플랫폼(머리)을 밀고 당깁니다. 6개 링크의 길이 조합으로 머리의 위치/자세 6자유도가 결정됩니다.
* **기구 파라미터**: 기구학 엔진은 `motor_arm_length`(모터 암 길이), `rod_length`(로드 길이), 각 모터의 배치 정보, `head_z_offset`(머리 기준 높이 오프셋)을 데이터(`kinematics_data.json`)로 읽어 계산합니다.
* **장점**: 병렬 구조라 직렬 로봇 팔보다 강성이 높고 하중을 여러 링크가 분산 지지해, 작은 모터로도 머리를 안정적으로 정밀 제어할 수 있습니다.

#### ④ 기구학(Kinematics) 구현

서브모듈에는 세 가지 기구학 엔진이 함께 제공됩니다.

* **해석적 기구학** — [analytical_kinematics.py](https://github.com/orocapangyo/reachy-mini): **역기구학(IK)은 해석적(닫힌 해) 방식**, **순기구학(FK)은 수치 해석(뉴턴법)** 으로 푼다. 성능을 위해 핵심 계산은 Rust로 구현(`reachy_mini_rust_kinematics`)되어 Python 바인딩으로 호출됩니다.
* **Placo 기반** — [placo_kinematics.py](https://github.com/orocapangyo/reachy-mini): 최적화 기반 기구학 라이브러리(Placo) 활용.
* **신경망 근사** — [nn_kinematics.py](https://github.com/orocapangyo/reachy-mini): 학습된 모델로 빠른 근사 계산.
* `automatic_body_yaw` 옵션으로 머리 목표 자세에 맞춰 몸통 yaw를 자동 분배하여, 머리만으로 부족한 회전 범위를 몸통이 보완하도록 설계되어 있습니다.

#### ⑤ 구동계(모터) 상세

모든 관절은 Robotis **Dynamixel** 스마트 서보(TTL 통신)로 구동되며, 한 버스에 데이지체인으로 연결됩니다.

| 부위 | 모터 | 수량 | 비고 |
| :--- | :--- | :---: | :--- |
| 몸통 베이스 | 커스텀 Dynamixel **XC330-M288-PG** | 1 | XC330-M288-T 기반 + 플라스틱 기어 |
| 안테나 | Dynamixel **XL330-M077-T** | 2 | 저토크·경량, 표현용 |
| 스튜어트 플랫폼 | Dynamixel **XL330-M288-T** | 6 | 머리 6-DOF 구동 |

> 모터가 **TTL 데이지체인**으로 연결되므로, 각 모터의 ID/연결 상태 점검이 중요합니다. 후술하는 `scan_motors` CLI 개선이 이 점검 과정을 돕습니다.

#### ⑥ 전장(電裝) 및 전원

* **파워 보드**: 입력 6.8–7.6V. (Wireless) **LiFePO4 배터리 2000mAh / 6.4V / 12.8Wh** 내장 — 과충전·과방전·과전류·단락 보호 및 온도 센서 포함.
* **컨트롤러 보드**
  * *Wireless*: **Raspberry Pi CM4104016**(WiFi, RAM 4GB, eMMC 16GB)을 탑재한 온보드 컨트롤러. Dynamixel TTL, 카메라 CSI, 마이크 어레이, USB-C 출력(주변기기 연결용, **충전 불가**)을 통합. WiFi는 2.4/5GHz 듀얼밴드 패치 안테나(2.79 dBi, 무지향).
  * *Lite*: 동일 인터페이스(TTL/CSI/마이크)를 갖되 **USB-C 입력으로 외부 PC에 연결**되는 형태(이 포트로 충전되지 않음).

#### ⑦ 센서 구성

* **카메라**: Raspberry Pi Camera v3 광각 — Sony **IMX708**, **12MP**, **120° 광각**, 오토포커스, CSI(DSI) 연결.
* **마이크 어레이**: PDM MEMS 디지털 마이크 **4개**, 최대 16kHz 샘플레이트 / -26 dBFS 감도 / 64 dBA SNR. Seeed Studio reSpeaker **XMOS XVF3800** 기반 → 음원 방향 추적(DoA)·빔포밍 지원.
* **스피커**: 5W @ 4Ω.

#### ⑧ 디지털 기구 자산(공개 CAD/모델)

* **URDF / MJCF 전체 로봇 모델**: [urdf/robot.urdf](https://github.com/orocapangyo/reachy-mini), [mjcf/reachy_mini.xml](https://github.com/orocapangyo/reachy-mini). 충돌(collision) 메시는 coarse/fine 2단계로 제공되어 시뮬레이션 정밀도/속도를 선택할 수 있습니다.
* **STL 메시 150여 종**: 스튜어트 암/로드/볼조인트, 바디(top/bottom/turning bowl), 헤드 셸, 안테나, 렌즈·카메라 캐리어, 베어링(85×110×13), 스피커 등. 파일명 규칙으로 **3D 프린트 부품(`*_3dprint.stl`)** 과 구매 부품을 구분합니다.
* **원본 CAD 공개**: 모델 빌드 설정([mjcf/config.json](https://github.com/orocapangyo/reachy-mini))에 **OnShape 퍼블릭 문서 링크**가 기록되어 있어, 원본 파라메트릭 CAD를 직접 열람할 수 있습니다.
* **좌표계 정의**: world frame / head frame이 문서와 모델에 정의되어, 머리 목표 자세를 4×4 변환 행렬(SE(3))로 지정합니다.

---

### 2. 미디어 백엔드의 대전환: GStreamer 및 WebRTC 최적화
> **관련 소스 위치**: [src/reachy_mini/media](https://github.com/orocapangyo/reachy-mini)

가장 큰 기술적 도약은 오디오와 비디오 스트리밍을 처리하는 **미디어 파이프라인의 전면 개편**입니다. 로봇–대시보드–클라이언트 사이의 실시간 상호작용 품질을 좌우하는 핵심 영역입니다.

#### ① GStreamer 표준 백엔드 도입
* **배경**: 기존 미디어 처리 백엔드는 네트워크 환경이나 클라이언트 OS 종류에 따라 잦은 끊김과 높은 자원 점유율 문제가 있었습니다.
* **해결**: 미디어 백엔드의 기본값을 **GStreamer**로 전환하여, 플랫폼이 제공하는 **하드웨어 가속(인코딩/디코딩)** 을 적극 활용하도록 했습니다.
* **효과**: 파이프라인을 GStreamer 엘리먼트 그래프로 표준화함으로써 디바이스 소스(카메라/마이크)부터 네트워크 송출까지를 일관된 구조로 다루게 되어, 백엔드 교체·디버깅·확장이 수월해졌습니다. 설치 안내는 [SDK/gstreamer-installation.md](https://github.com/orocapangyo/reachy-mini) 참고.
* **호환성 모드 튜닝**: 대시보드 앱 실행 시 디바이스·환경에 따라 미디어 백엔드가 즉시 호환성 모드로 동작할 수 있도록, 데몬 내부의 세부 실행 인자가 대거 튜닝되었습니다.

#### ② WebRTC 양방향 오디오(Bidirectional Audio) 아키텍처 및 Latency 단축
* **양방향 오디오**: 기존의 단방향 스트리밍에서 완전히 탈피하여, 로봇의 스피커로 클라이언트의 음성을 출력하고 동시에 로봇 마이크 입력을 가져오는 **실시간 양방향 오디오 통신**이 탑재되었습니다. 대화형 애플리케이션(음성 비서 등)의 기반이 됩니다.
* **성능 최적화**:
  - **버퍼 복사 제거**: 미디어 관리에서 불필요한 버퍼 복사(Buffer Copy) 단계를 없애 메모리 오버헤드와 CPU 점유율을 대폭 낮췄습니다. (제한된 CM4 자원에서 특히 효과적)
  - **Opus 인코더 레이텐시 최적화**: 무선 연결 시 소리가 밀리는 현상을 크게 최소화. 코덱 단계의 지연이 전체 왕복 지연에 미치는 영향이 커, 인코더 설정 조정만으로 체감 응답성이 개선됩니다.
  - **메인 루프 차단 해소**: WebRTC 비동기 호출 시 메인 루프가 차단(Block)되던 문제를 **쓰레드 풀(Threaded Loop)** 구조 도입으로 해결해, 스트리밍 중에도 제어 루프가 끊기지 않도록 했습니다.

```python
# WebRTC 오디오 백엔드 — 비동기 통신을 별도 스레드 풀에서 구동해 메인 루프 차단 방지
def start_webrtc_loop():
    loop = asyncio.new_event_loop()
    t = Thread(target=loop.run_forever)
    t.start()
    # 양방향 오디오 파이프라인 등록 (제로카피 버퍼 전달)
```

#### ③ 오디오 장치 디텍션 및 디바이스 공유 보완
* **PipeWire 기반 디바이스 공유**: 카메라·마이크 스트림을 PipeWire 환경으로 유도하여, **로봇 제어 데몬과 사용자 앱이 동시에 같은 입력 장치에 접근**할 수 있도록 했습니다(독점 방지).
* **PulseAudio 폴백 확장**: 비-PipeWire(일반 PulseAudio) 구형 배포판 환경에서도 오디오 디렉팅이 에러 없이 폴백되도록 탐지 로직을 최적화하여, 배포판/사운드 서버 차이로 인한 인식 실패를 줄였습니다.
* **Sound DoA 무선 지원**: 마이크 어레이(reSpeaker XVF3800)의 카드 번호를 인식해 소리 나는 방향을 식별하고 머리를 돌리는 **음원 방향 추적(DoA)** 의 무선 모드 지원을 강화했습니다. 재생 예제는 [sound_doa.md](https://github.com/orocapangyo/reachy-mini) 참고.

---

### 3. 하드웨어 안정성 및 모터 제어 최적화
> **관련 소스 위치**: [src/reachy_mini/io](https://github.com/orocapangyo/reachy-mini) 및 [src/reachy_mini/kinematics](https://github.com/orocapangyo/reachy-mini)

앞서 본 Dynamixel 구동계와 스튜어트 메커니즘을 **오래·안전하게** 굴리기 위한 제어 로직이 대거 수정되었습니다. 핵심은 "불필요한 마모를 줄이고, 비정상 상황에서 기구를 보호한다"입니다.

#### ① 부팅 시 모터 무조건 재플래싱(Systematic Reflash) 제거
* **기존 문제**: 로봇 서비스나 데몬이 켜질 때마다 연결된 모든 Dynamixel 모터의 펌웨어 구성을 새로 플래싱(Reflash)하여, **부팅 시간 연장(30초 이상)**, EEPROM 수명 단축, 하드웨어 내구도 하락을 일으켰습니다.
* **해결**: 데몬 기동 시 모터의 현재 파라미터를 먼저 고속 스캔하고, **구성이 불일치하는 모터에 대해서만 부분 플래싱**을 실행하도록 지능형 설정 검증을 도입했습니다.
* **효과**: 정상 구성에서는 플래싱을 생략해 **약 1초 만에 기동**하고, EEPROM 쓰기 사이클을 아껴 하드웨어 수명을 늘립니다.

> 부팅 시 데몬 시작 → 모터 파라미터 체크 → **일치하면** 플래싱 생략(즉시 기동) / **불일치하면** 해당 모터만 부분 플래싱 → 로봇 가동 준비 완료.

#### ② 안전 잠금 장치 및 전력 차단 버그 대응
* **모터 토크 제어(낙하 방지)**: 애플리케이션이나 대시보드를 닫을 때, 토크가 풀려 머리/링크가 중력으로 떨어지며 스튜어트 기구가 파손되는 것을 막기 위해, **앱 종료와 동시에 모터 토크가 즉시 강제 활성화(`enable_torque`)** 되어 자세를 유지하도록 수정했습니다.
* **전원 보호 회로 오작동 해결**: 특정 모터에 과부하가 걸렸을 때 과전류 센서가 지나치게 예민하게 반응하여 **시스템 전체 전원(GPIO 핀 제어)이 즉시 차단**되던 문제를, 하드웨어 전력 수준(신형 전원 어댑터 출력)에 맞춰 안전 마진을 재보정했습니다.

#### ③ 모터 검사용 CLI 도구 고도화
* TTL 데이지체인 특성상 모터 ID/연결 점검이 잦은데, `scan_motors` 명령어에 **`--wireless`** 및 **`--port`** 옵션을 추가했습니다.
* 이를 통해 무선(온보드) 환경이나 멀티 포트 인터페이스에서도 터미널에서 신속하게 **연결된 모터 ID와 상태**를 확인할 수 있어, 9개 서보 중 어느 것이 응답하지 않는지 현장에서 바로 진단할 수 있습니다.

```bash
# 무선 모드 또는 특정 시리얼 포트를 직접 지정해 모터 점검
scan_motors --wireless --port /dev/ttyUSB0
```

* **ID 기반 단독 셋업**: 특정 모터를 단독 지정할 때 모터 이름(name)을 거치지 않고 **순수 하드웨어 ID로만 매핑**하도록 하여, 명칭 충돌 문제를 근본적으로 해소했습니다.

---

### 4. 멀티 OS 지원 및 개발 생산성 도구
> **관련 소스 위치**: [src/reachy_mini/apps](https://github.com/orocapangyo/reachy-mini) 및 [src/reachy_mini/daemon](https://github.com/orocapangyo/reachy-mini)

Reachy Mini 환경은 웹 대시보드와 로컬 데스크톱(또는 외부 PC, 특히 Lite)을 연결해 동작하므로, 개발 환경 호환성과 생산성 도구가 중요합니다.

#### ① Windows 플랫폼 풀 체인 지원
* **임시 폴더 정리 실패 해결**: Windows에서 빌드 도중 임시 파일을 닫지 않아 발생하던 파일 잠김·디렉터리 삭제 에러(`PermissionError`)를, **컨텍스트 매니저**로 임시 자원이 안전하게 폐기되도록 수정했습니다.
* **경로 인코딩 오류 수정**: 프로젝트 생성 시 이모지·특수 문자가 포함된 파일 경로로 인해 발생하던 **`UnicodeEncodeError`** 를 전면 정비했습니다.
* **네트워크 IP 파싱 수정**: Windows에서도 데몬이 네트워크 IP를 올바르게 검색·파싱하도록 `get_ip_address`의 플랫폼 의존 코드를 보정했습니다. (대시보드 접속 주소 안내에 직접 영향)

#### ② App Assistant 성능 및 템플릿 강화
* 대시보드 앱스토어에서 커뮤니티 앱 개발을 돕는 **`reachy-mini-app-assistant`** 도구를 업데이트했습니다.
* 대화형 동작 앱을 위해 **`--template conversation`** 구조를 추가하고, 패키지 네이밍 충돌을 막는 고유 접미사 부여 로직을 더했습니다.
* 웹 대시보드 안에서 독립 가상환경을 초기화·재구축하는 **Virtual Environment Reset** 기능을 UI 버튼("Reset Venv")으로 통합해, 라이브러리 충돌로 앱 구동이 불가할 때 브라우저 클릭만으로 복구할 수 있습니다.

```bash
# 대화형 앱 템플릿으로 로봇 앱 스켈레톤 생성
reachy-mini-app-assistant create --template conversation
```

#### ③ 관련 개발 문서
* 환경 구축·운용은 [get_started.md](https://github.com/orocapangyo/reachy-mini), [usage.md](https://github.com/orocapangyo/reachy-mini), [development_workflow.md](https://github.com/orocapangyo/reachy-mini)에 정리되어 있으며, 앱 개발 지침은 서브모듈 루트 [AGENTS.md](https://github.com/orocapangyo/reachy-mini)에서 확인할 수 있습니다.

---

### 5. 요약 및 정리

이번 1년간의 변경 내역과 하드웨어 구성을 종합하면 다음 네 가지로 귀결됩니다.

1. **검증된 기구 플랫폼**: 9 자유도(머리 6 + 몸통 1 + 안테나 2)와 **스튜어트 병렬 메커니즘**, Dynamixel 구동계, CM4 기반 전장이 URDF/MJCF·STL·OnShape로 **완전히 공개**되어 있어, 학습·시뮬레이션·확장이 자유롭습니다.
2. **지연 시간 단축 (Low Latency)**: GStreamer 표준화와 WebRTC 양방향 오디오, 버퍼 복사 제거·Opus 최적화·쓰레드 풀 도입으로 상호작용 응답성이 크게 향상되었습니다.
3. **하드웨어 내구성·안전성 증대**: 조건부 플래싱으로 모터 쓰기 마모를 줄이고, 종료 시 토크 홀드로 기구 낙하·파손을 방지하며, 전원 보호 회로 오작동을 보정했습니다.
4. **크로스 플랫폼 개발 활성화**: Windows 풀체인 지원과 App Assistant·Venv Reset, 그리고 **마이크 케이블 교체 가이드** 등 트러블슈팅 문서 보강으로, 윈도우 PC에서도 로봇 앱을 손쉽게 개발·검증하는 사이클을 마련했습니다.

---

> [!TIP]
> **학습 제안**:
> 1. 먼저 [hardware.md](https://github.com/orocapangyo/reachy-mini)와 OnShape 원본 CAD로 **기구 구조(스튜어트 플랫폼)** 를 이해하고,
> 2. [src/reachy_mini/kinematics](https://github.com/orocapangyo/reachy-mini)의 해석적 IK 코드와 URDF 모델을 대조해 **기구학 ↔ 형상**의 연결을 확인한 뒤,
> 3. [examples](https://github.com/orocapangyo/reachy-mini)의 `look_at`·`sound_doa`·`imu` 등 최신 예제를 직접 구동해 **소프트웨어 변경(미디어·모터 제어)** 의 효과를 체감해 보시길 권장합니다.
