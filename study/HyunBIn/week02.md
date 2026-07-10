# 2주차 : 기본 동작 제어 

---

## 시작하기 전에 : 시뮬레이션 환경 준비

### 빠른 시작 (이미  week 01을 완료한 경우)

```bash

# 1. 프로젝트 디렉토리로 이동
cd reachy_mini_project

# 2. 가상환경 활성화 (Windows)
.venv\Scripts\activate

# 3. 시뮬레이션 데몬 실행
reachy-mini-daemon --sim

# 4. 브라우저에서 확인
# http://localhost:8000 접속

```

### VS CODE 설치 : CMD 창에서 수정이 어려워서..

```bash

# 1. VS Code 및 파이썬 설치
프로그램 설치할 때 ('Add python to PATH' 옵션 체크 필수!)
# 2. 파이썬 확장 기능 설치
 - VS Code를 켭니다.
 - 왼쪽 사이드바에서 **네모 4개 모양 아이콘(Extensions)**을 클릭합니다.
 - 검색창에 Python을 입력합니다.
 - Microsoft에서 만든 Python 확장 프로그램을 찾아 **Install(설치)**을 누릅니다.
# 3.  작업 폴더 열고 파일 만들기
- 상단 메뉴에서 File -> Open Folder...를 눌러 코드를 저장할 폴더를 하나 선택합니다.
- 폴더가 열리면 왼쪽 탐색기 빈 곳을 우클릭하거나 New File 아이콘을 눌러 파일을 만듭니다.
- 파일 이름은 robot_test.py처럼 끝에 꼭 **.py**를 붙여서 만들어 줍니다.
# 4.  실행
- 로봇 제어용 라이브러리(reachy_mini)가 컴퓨터에 깔려있어야 코드가 작동합니다.
- VS Code 상단 메뉴에서 Terminal -> New Terminal을 엽니다. (화면 아래에 검은 창이 뜹니다)
- 터미널 창에 'pip install reachy-mini' 명령어를 입력하고 엔터를 누릅니다.
- 화면 우측 상단에 있는 **세모 모양의 재생 버튼(Run Python File)**을 클릭하면 코드가 실행됩니다!

```

---

##  1. 머리 동작 제어

### 머리를 왼쪽으로 10mm 이동
<img width="300" height="300" alt="image" src="https://github.com/user-attachments/assets/e5f4ea40-a361-4069-891c-df93162b6b08" />
---
## 2. 회전동작

### 2.2 머리를 위로 10mm 들고(z축) 롤(roll) 15eh 회전
<img width="800" height="500" alt="2-2 2" src="https://github.com/user-attachments/assets/8382a249-3b90-41e7-88d1-59eb7c20f0b3" />

### 2.3 다양한 회전 조합(고개를 끄덕이는동작, 좌우로 돌리는 동작, 위를 보면서 왼쪽으로 돌리기)
<img width="800" height="500" alt="2-2 3" src="https://github.com/user-attachments/assets/507f7747-f045-4d56-bdfe-5c0a94c81f1f" />

---

## 3. 안테나 제어

### 3.2 양쪽 안테나를 45도로 이동후 복귀
<img width="800" height="500" alt="2-3 2" src="https://github.com/user-attachments/assets/f0b4d9ee-0094-4387-b257-7f5b80e7b2be" />

### 3.3 비대칭 안테나 동작
<img width="800" height="500" alt="2-3 3" src="https://github.com/user-attachments/assets/c521e1ce-06ad-41f5-a772-6270d1b277e6" />

---

## 7. GitHub 저장소 예제 코드 분석

### 7.2 시퀀스 예제 (Yaw 회전 / 좌우로 고개 돌리기)
<img width="800" height="500" alt="2-7 2" src="https://github.com/user-attachments/assets/fdcd4dd8-3ab1-4830-92d3-888ff5f58e70" />

### 7.2 시퀀스 예제 (Pitch 회전 / 끄덕이기)
<img width="800" height="500" alt="7-7 2(끄덕이기)" src="https://github.com/user-attachments/assets/b645d630-99b5-400d-8e51-66a2f862c464" />

### 7.2 시퀀스 예제 (Roll 회전 / 좌우로 기울이기)
<img width="800" height="500" alt="7-7 2(좌우로 기울이기)" src="https://github.com/user-attachments/assets/933893c5-3960-48f4-b7b2-ee2abed8e236" />

### 7.2 시퀀스 예제 (상하이동 / Z축 평행이동)
<img width="800" height="500" alt="7-7 2(Z축평행이동)" src="https://github.com/user-attachments/assets/2b0cf8eb-7b5b-42b3-8553-c4da582c6ea6" />

### 7.2 시퀀스 예제 (안테나 비대칭 움직임 / 양 쪽 안테나가 반대 방향으로)
<img width="800" height="500" alt="7-7 2(안테나 비대칭)" src="https://github.com/user-attachments/assets/7bbc4287-28ec-4b25-85d0-a0f1643f564a" />

### 7.2 시퀀스 예제 (원형 움직임 / X-Y 평면, 5초 동안 원형 경로로 머리 이동)
<img width="800" height="500" alt="7-7 2(원형 움직임)" src="https://github.com/user-attachments/assets/de901f9f-142d-4e00-a36d-1863d6067e10" />

### 7.3 비전 기반 제어 (카메라 이미지에서 클릭한 지점을 로봇이 바라보도록)
<img width="800" height="500" alt="7-7 3(비전기반제어)" src="https://github.com/user-attachments/assets/852df53b-9e0e-47b0-8906-d61993b6f2d2" />

---

## 8. 과제

### 과제1 : 8자 패턴으로 머리 움직이기
#### 도전과제:
  ##### - 8자의 크기를 변경할 수 있도록 파라미터화
  ##### - 8자를 그리는 속도 조절 기능 추가
  ##### - 역방향으로도 8자 그리기
<img width="800" height="500" alt="8-8 1(8자패턴 도전과제)" src="https://github.com/user-attachments/assets/20a2e8cf-c30c-41f7-a247-9b2eb6d2acce" />


### 소스코드
```python
import numpy as np
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

# ===== 파라미터 =====
width = 30      # 가로 크기(mm)
height = 5     # 세로 크기(mm)
num_points = 50 # 점 개수
duration = 0.5  # 이동 시간
reverse = False

with ReachyMini() as mini:

    for i in range(num_points):
        t = 2 * np.pi * i / num_points

        if reverse:
            t = -t

        # 8자 궤적
        y = width * np.sin(t)
        z = height * np.sin(2 * t)

        pose = create_head_pose(y=y, z=z, mm=True)
        mini.goto_target(head=pose, duration=duration)

    mini.goto_target(head=create_head_pose(), duration=1.0)
```

### 과제2 : 감정 표현하기
#### 도전과제:
  ##### - 머리 움직임과 결합하여 더 풍부한 감정 표현 ...ok
  ##### - 추가 감정 구현(두려움, 자신감, 혼란 등)
  ##### - 감정 전환 애니메이션 추가

  ### 소스코드
  
```python
import numpy as np
import time
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose
from scipy.spatial.transform import Rotation as R

def express_joy(mini):
    """기쁨: 안테나를 빠르게 위아래로"""
    for _ in range(3):
        mini.goto_target(antennas=np.deg2rad([60, 60]), duration=0.3)
        mini.goto_target(antennas=np.deg2rad([30, 30]), duration=0.3)
    mini.goto_target(antennas=[0, 0], duration=1.0)

def express_sadness(mini):
    """슬픔: 안테나를 천천히 내리기"""
    mini.goto_target(antennas=np.deg2rad([10, 10]), duration=3.0)
    time.sleep(2)
    mini.goto_target(antennas=[0, 0], duration=2.0)

def express_surprise(mini):
    """놀람: 안테나를 갑자기 펼치기"""
    s = time.time()
    t0 = time.time()

    #시작 전 초기 위치 설정
    mini.goto_target()
    #2초 동안 실행 루프
    while time.time() - s < 2.0:
        t = time.time() - t0
        #1. 머리 위치 계산(z축 평행이동)
        pose = np.eye(4)  # 4x4 단위 행렬로 초기화
        pose[:3, 3][2] += 0.025 * np.sin(2 * np.pi * 0.5 * t)  # z축 평행이동
        
        if t <0.2:
            antenna_angle = [0,0]

        elif 0.2 <= t<0.4:
            antenna_angle = np.deg2rad([80,80])
        elif 0.4<= t< 1.2:
            antenna_angle = np.deg2rad([80,80])
        else:
            antenna_angle = [0,0]
        
        mini.set_target(head=pose, antennas=antenna_angle)

        time.sleep(0.01)
        
def express_curiosity(mini):
    """호기심: 안테나를 번갈아 움직이기"""
    for _ in range(2):
        mini.goto_target(antennas=np.deg2rad([45, 0]), duration=0.5)
        mini.goto_target(antennas=np.deg2rad([0, 45]), duration=0.5)
    mini.goto_target(antennas=[0, 0], duration=1.0)

def express_anger(mini):
    """화남: 안테나를 빠르고 강하게 움직이기"""
    for _ in range(4):
        mini.goto_target(antennas=np.deg2rad([70, 70]), duration=0.2)
        mini.goto_target(antennas=np.deg2rad([20, 20]), duration=0.2)
    mini.goto_target(antennas=[0, 0], duration=1.0)

def express_emotion(mini):
    

# 사용 예시
with ReachyMini() as mini:
    print("기쁨 표현")
    express_joy(mini)
    time.sleep(1)

    print("슬픔 표현")
    express_sadness(mini)
    time.sleep(1)

    print("놀람 표현")
    express_surprise(mini)
    time.sleep(1)

    print("호기심 표현")
    express_curiosity(mini)
    time.sleep(1)

    print("화남 표현")
    express_anger(mini)
```



















