## 3주차 : 고급 동작 제어

### 학습 목표
  - 다양한 보간 방법 활용
  - 실시간 동작 제어
  - 모터 상태 관리
---

  ## 1. 다양한 보간 방법
  ### 1.1 보간이란?

  보간은 시작 위치에서 목표 위치까지 로봇 관절을 부드럽게 이동시키는 기법, Reachy Mini는 여러 보간 방법을 지원

  ### 1.2 선형 보간(Linear Interpolation)
  가장 기본적인 보간 방법으로, 시작점과 끝점을 직선으로 연결합니다.
  ** 특징 **
  - 단순하고 예측 가능
  - 속도가 일정
  - 급격한 시작/정지로 인한 떨림 가능

    <img width="800" height="500" alt="1 2" src="https://github.com/user-attachments/assets/976c4323-7285-4a71-9cc8-558c4a5afb02" />

### 1.3 최소 저크 보간(Minimum Jerk)
부드러운 가속과 감속을 제공하여 자연스러운 움직임을 만듭니다.
 ** 특징 **
 - 부드러운 시작과 종료
 - 가속도 변화(Jerk)를 최소화
 - 인간과 유사한 자연스러운 움직임
 - 로봇 관절에 부담 감소

### 1.4 보간 모드 비교

<img width="1108" height="1031" alt="1 4 보간모드 비교" src="https://github.com/user-attachments/assets/a16bff5b-61b5-4ab4-8721-d2fd39ee1cf7" />

## 2. 실시간 동작 제어
### 2.1 블로킹 제어(goto_target)
`goto_target`은 지정된 시간(`duration`) 동안 보간을 통해 부드럽게 목표 자세로 이동하며, 동작이 완전히 완료될 때까지 함수 호출이 대기(blocking)됩니다.

<img width="893" height="843" alt="2 1" src="https://github.com/user-attachments/assets/0d24be2e-410b-4e1b-9e62-8e9f4fcfbf4f" />

### 2.2 실시간 비블로킹 제어(set_target)
실시간 추종이나 궤적 제어와 같이 정지 없이 연속적으로 위치를 업데이트할 때는 `set_target`을 사용합니다. `set_target`은 즉시 명령을 전송하고 대기 없이 즉시 리턴하므로, 루프문 내에서 짧은 주기(예: 10ms~20ms)로 호출하여 실시간 동작을 수행할 수 있습니다.

<img width="800" height="500" alt="2 2" src="https://github.com/user-attachments/assets/85f12cbb-33e4-4901-84cf-4ac70b3181c7" />


### 2.3 동시 다중 부위 제어
`goto_target` 이나 `set_target` 호출 시 `head`와 `antennas`, `body_yaw` 인자를 조합하여 머리, 안테나, 바디 요를 동시에 제어할 수 있습니다.

<img width="800" height="500" alt="2 3" src="https://github.com/user-attachments/assets/ef8ff006-07d8-4c0c-a2e3-3e73a960c1bd" />

### 2.4 연속 동작 시퀀스
동작들을 순차적으로 연달아 수행할 때는 `goto_target`을 루프나 시퀀스 형태로 정의하여 활용할 수 있습니다.

<img width="800" height="500" alt="image" src="https://github.com/user-attachments/assets/4a12a8e4-9bd7-48a3-80db-1047450fed82" />

## 4. 종합 실습 예제
### 4.1 부드러운 헤드 트래킹

<img width="1274" height="1087" alt="4 1" src="https://github.com/user-attachments/assets/480771ed-7314-4160-ba11-a8b64eee27f4" />

## 5. 스튜어트 플랫폼 모터 구조
### 5.1 스튜어트 플랫폼이란?

스튜어트 플랫폼은 6개의 선형 액추에이터를 사용하여 6자유도 움직임을 구현하는 병렬 로봇 메커니즘 입니다.
**주요특징**
- 6개의 모터 사용
- 높은 강성과 정밀도
- 컴팩트한 크기에서 복잡한 움직임 구현
- 각 모터가 협력하여 최종 자세 제어
- 
### 5.5 역기구학
목표 자세가 주어지면, 각 모터의 각도를 계산

### 5.6 정기구학
6개 모터의 각도로부터 헤드의 최종 포즈를 역산

### 5.7 솔루션 패턴의 의미
각 모터는 'solution' 값이 0 또는 1로 설정, 역기구학 계산시 여러 해가 존재할 때 어떤 해를 선택할지 결정

## 6. 실습 과제
### 과제1 : 보간 방법 비교

<img width="800" height="800" alt="6 1" src="https://github.com/user-attachments/assets/f22a7546-7e3c-4afc-9bc0-07327f433f82" />

- linear : 스무스한듯 하지만 빠름
- min jerk : 스무스함 가감속이 확실히 느껴짐
- ease in out : 어느정도 스무스 한것 같음
- cartoon : 부서질 수준으로 움직임

  
