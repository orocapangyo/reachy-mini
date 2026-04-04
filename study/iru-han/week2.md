# 1. 머리를 왼쪽으로 이동
```
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose
import numpy as np


with ReachyMini() as mini:
    # 머리를 왼쪽으로 이동 (y축 -10mm)
    pose = create_head_pose(y=-10, mm=True)
    mini.goto_target(head=pose, duration=2.0)

    # 초기 위치로 복귀
    pose = create_head_pose()
    mini.goto_target(head=pose, duration=2.0)
```
<img width="381" height="703" alt="image" src="https://github.com/user-attachments/assets/731b2b61-fac6-47ba-88e4-38087dff7676" />

# 2. 머리를 위로 들고 z축 롤 회전
```
from reachy_mini.utils import create_head_pose
import numpy as np


with ReachyMini() as mini:
    
    # 머리를 위로 들고(z축) 롤(roll) 회전
    pose = create_head_pose(z=10, roll=15, degrees=True, mm=True)
    mini.goto_target(head=pose, duration=2.0)

    # 초기 위치로 복귀
    pose = create_head_pose()
    mini.goto_target(head=pose, duration=2.0)
```
<img width="407" height="742" alt="image" src="https://github.com/user-attachments/assets/533f671e-a1b2-4535-829c-70a7f365aa6c" />

# 3. 안테나 제어
```
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose
import numpy as np

with ReachyMini() as mini:
    
    # 양쪽 안테나를 45도로 이동
    mini.goto_target(antennas=np.deg2rad([45, 45]), duration=1.0)

    # 초기 위치로 복귀
    mini.goto_target(antennas=[0, 0], duration=1.0)

```
<img width="427" height="709" alt="image" src="https://github.com/user-attachments/assets/da496590-14cb-40ca-838e-c3dcc2455934" />

# 4. 복합 동작
```
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose
import numpy as np

with ReachyMini() as mini:
    
    mini.goto_target(
        head=create_head_pose(y=-10, mm=True),
        antennas=np.deg2rad([45, 45]),
        body_yaw=np.deg2rad(30),
        duration=2.0
    )

    pose = create_head_pose()
    mini.goto_target(head=pose, duration=2.0)
    
    # 초기 위치로 복귀
    mini.goto_target(antennas=[0, 0], duration=1.0)
```
<img width="460" height="690" alt="image" src="https://github.com/user-attachments/assets/6ed961ba-1879-4028-ba60-4603e1cb1b30" />

## 8자 패턴(Lissajous Curve)의 원리
머리를 8자 형태로 움직이려면 좌우(Roll/Yaw) 움직임과 상하(Pitch) 움직임의 주기를 다르게 설정해야 합니다. 보통 다음과 같은 삼각함수 식을 사용합니다.<br/>
<img width="146" height="100" alt="image" src="https://github.com/user-attachments/assets/56c7c658-61e4-4921-8156-ed44fe95a182" />
여기서 t는 시간(또는 각도)이며, B 방향의 주기를 A보다 두 배 빠르게 설정하면 우리가 아는 8자 모양(infty)이 만들어집니다.<br/>

## 감정별 안테나 각도 설정 가이드
리치미니의 안테나는 각도에 따라 다음과 같은 느낌을 줄 수 있습니다. (단위: Degree)
<img width="497" height="102" alt="image" src="https://github.com/user-attachments/assets/e70fdf83-f0a4-4258-a5be-172f9dd01c91" />

# 5. 리치미니 감정 표현
```
import numpy as np
import time
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

def move_8_pattern(robot, duration=5.0, emotion='joy'):
    start_time = time.time()
    print(f"현재 감정 모드: {emotion}")

    while (time.time() - start_time) < duration:
        t = time.time() - start_time
        
        # 기본 설정값 (감정에 따라 바뀔 변수들)
        speed = 1.0          # 움직임 속도
        pitch_offset = 0     # 고개 높낮이 기준 (0은 정면)
        antenna_pos = [0, 0] # 안테나 기본 위치
        
        if emotion == 'joy':
            # [기쁨] 속도 빠름 + 안테나 마구 흔들기(고주파 sine파)
            speed = 1.5
            pitch_offset = -5  # 살짝 위를 봄
            # 안테나를 40도 기준으로 +- 30도씩 빠르게 흔듦 (20배속 박자)
            shake = 30 * np.sin(2 * np.pi * 5.0 * t) 
            antenna_pos = np.deg2rad([-40 - shake, 40 + shake])

        elif emotion == 'sad':
            # [슬픔] 속도 매우 느림 + 고개 푹 숙임
            speed = 0.4
            pitch_offset = 25  # 고개를 아래로 (양수값)
            antenna_pos = np.deg2rad([-150, 150]) # 안테나 푹 내림

        elif emotion == 'surprise':
            # [놀람] 고개 바짝 들기 + 안테나 바짝 세우기
            speed = 0.0
            pitch_offset = -30 # 고개를 위로 (음수값)
            antenna_pos = np.deg2rad([50, -50]) # 안테나 수직

        # 8자 패턴 계산 (speed를 곱해 리듬 조절)
        roll = 15 * np.sin(2 * np.pi * 0.5 * speed * t)
        # pitch_offset을 더해 고개 높낮이 기본값을 고정함
        pitch = 10 * np.sin(2 * np.pi * 1.0 * speed * t) + pitch_offset
        
        robot.goto_target(
            head=create_head_pose(roll=roll, pitch=pitch),
            antennas=antenna_pos,
            duration=0.1
        )
        time.sleep(0.05)

# 실행부
with ReachyMini() as mini:
    # 1. 기쁨: 빠르게 8자 + 안테나 파르르
    move_8_pattern(mini, duration=4.0, emotion='joy')
    time.sleep(0.5)

    # 2. 슬픔: 천천히 8자 + 고개 숙임
    move_8_pattern(mini, duration=5.0, emotion='sad')
    time.sleep(0.5)

    # 3. 놀람: 고개 바짝 들고 8자
    move_8_pattern(mini, duration=3.0, emotion='surprise')

    # 복귀
    mini.goto_target(head=create_head_pose(), antennas=[0, 0], duration=1.5)
```


https://github.com/user-attachments/assets/87f03daa-b06e-46e5-970b-9d9227bbf9a6


