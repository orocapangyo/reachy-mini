## 3주차: 고급 동작 제어

### 학습 목표

- Reachy Mini 기구학 이해
- 다양한 보간(interpolation) 이해 및 활용
- 실시간 동작 제어
- 모터 상태 관리

---

## 1. Reachy Mini 기구학 이해
### 1.1 Moving the Header

Reachy Mini는 Stewart Platform 목 구조는 생명체와 유사한 동작을 가능하게 하며, 6자유도로 pitch, roll, yaw를 포함한 자연스러운 머리 움직임을 구현되고, 추가적으로 360도 베이스 회전과 2개의 안테나 움직임으로 구성된다.

- translation :
	- X axis - 앞 뒤 움직임
	- Y axis - 좌 우측 움직임
	- Z axis - 위 아래 움직임
	![](Pasted%20image%2020260322005929.png)
- rotation :
     - Roll - Tilting (Rotation around the X-axis)
     - Pitch - Nodding up/down (Rotation around the Y-axis)
     - Yaw -  Shaking left/right (Rotation around the Z-axis)
	![](Pasted%20image%2020260322010034.png)
  
### 1.2 Moving the Antennas

2개의 안테나는 개별로 동작하며 개별 각도 값으로 제어된다. 
![339](Pasted%20image%2020260322013004.png|342)
### 1.3 Moving the Base

2개의 안테나는 개별로 동작하며 개별 각도 값으로 제어된다. 
![340](Pasted%20image%2020260322013043.png|343)
## 2.  다양한 보간(Interpolation) 방법 이해 및 활용
### 2.1 Reachy Mini 기본 이동 함수

아래 goto_target 함수로 보간 방법은 linear, minjerk, ease or cartoon으로 4가지 설정이 가능하며 기본값으로는 minjerk이다. 따라서 method 설정 없이 이동할 경우 minjerk 보간이 적용된다. 

```python
    def goto_target(
        self,
        head: Optional[npt.NDArray[np.float64]] = None,  # 4x4 pose matrix
        antennas: Optional[
            Union[npt.NDArray[np.float64], List[float]]
        ] = None,  # [right_angle, left_angle] (in rads)
        duration: float = 0.5,  # Duration in seconds for the movement, default is 0.5 seconds.
        method: InterpolationTechnique = InterpolationTechnique.MIN_JERK,  # can be "linear", "minjerk", "ease" or "cartoon", default is "minjerk")
        body_yaw: float | None = 0.0,  # Body yaw angle in radians
    )
```

### 1.2 보간이란?

보간은 시작 위치에서 목표 위치까지 로봇 관절을 부드럽게 이동 시키는 기법입니다. Reachy Mini는 여러 보간 방법을 지원합니다.
![](Pasted%20image%2020260322135543.png)
![[velocity_constrained_vmax_correct_peaks.html]]
#### 1.2.1 선형 보간 (Linear Interpolation)

가장 단순한 방법으로, `s(t) = t`야. 속도는 상수 1이고 가속도는 0이고 시작하는 순간 즉시 최대 속도, 멈추는 순간 즉시 정지하기 때문에 시작과 끝에서 속도 불연속이 발생한다. 따라서 이런 불연속은 서보 모터에 순간적 충격(jerk → 무한대)을 가하기 때문에, 실제 로봇에서는 모터가 떨리고 기계적 충격이 크다.

```python
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

reachy = ReachyMini()
reachy.goto_target(
    head=create_head_pose(pitch=20, yaw=15),
    duration=2.0,
    method='linear'
)
```

#### 1.2.2 최소 저크 보간 (Minimum Jerk)

`s(t) = 10t³ - 15t⁴ + 6t⁵`로, 시작과 끝에서 속도 _그리고_ 가속도가 모두 0이 되도록 설계된 5차 다항식이다. "jerk"는 가속도의 시간 미분(d³x/dt³)인데, 이 프로파일은 전체 구간에서 jerk의 적분값을 최소화한다. 인간 뇌과학 연구에서 사람의 팔 도달 운동(reaching movement)이 이 프로파일을 따른다는 것이 Hogan(1984)에 의해 밝혀졌어. 그래서 Reachy Mini SDK에서 로봇이 "인간처럼" 자연스럽게 움직이기 위해 기본 설정으로 사용한다.

```python
reachy = ReachyMini()
reachy.goto_target(
    head=create_head_pose(pitch=-10, yaw=-10),
    duration=2.0,
    method='minimum_jerk'
)
```

#### 1.2.3 Cubic in-out 보간 (Ease)

CSS animation의 `ease-in-out`과 동일한 개념으로, 3차 다항식 두 개를 결합한 거야. 전반부(`t < 0.5`)는 `4t³`으로 천천히 가속하고, 후반부는 `1 - (-2t+2)³/2`로 천천히 감속해. 속도 프로파일이 종 모양(bell curve)에 가까워서 "부드럽다"고 느끼지만, 가속도가 시작/끝에서 정확히 0이 되지 않아. 웹 UI 전환에는 충분하지만, 로봇 관절에는 약간의 충격이 남아.

```python
reachy = ReachyMini()
reachy.goto_target(
    head=create_head_pose(pitch=-10, yaw=-10),
    duration=2.0,
    method='ease'
)
```

**특징:**
- 
### 1.4 보간 모드 비교(test1.py)

```python
import time
import numpy as np
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

# linear, minjerk, cartoon, ease 비교
methods = ["linear", "minjerk", "cartoon", "ease"]

with ReachyMini(media_backend="no_media") as mini:
    mini.goto_target(create_head_pose(), antennas=[0.0, 0.0], duration=1.0)
    try:    
        for method in methods:
            print(f"방법: {method}")
            mini.goto_target(
                head=create_head_pose(y=10, mm=True),
                duration=2.0,
                method=method
            )
            time.sleep(1)
            mini.goto_target(head=create_head_pose(), duration=2.0, method=method)
            time.sleep(1)
    except KeyboardInterrupt:
        pass

```

---

## 2. 실시간 동작 제어

### 2.1 x, y 축 sine 파형 실시간 동작 및 현재 위치 출력(test2.py)

```python
import time
import numpy as np

# X, Y축 사인파 궤적 추종
with ReachyMini() as mini:
    mini.set_target(head=create_head_pose())
    start = time.time()

    while True:
        t = time.time() - start
        if t > 10:
            break

        x = 10 * np.sin(2 * np.pi * 0.5 * t)
        y = 10 * np.sin(2 * np.pi * 0.5 * t)
        mini.set_target(head=create_head_pose(y=y, x=x, mm=True))
        time.sleep(0.01)

        # 현재 위치 출력
        current_x = mini.get_current_head_pose()[0][3]
        current_y = mini.get_current_head_pose()[1][3]
        current_z = mini.get_current_head_pose()[2][3]
        print(f"Current x: {current_x}, Current y: {current_y}, Current z: {current_z}")        

```

---

## 3. 모터 상태 관리

### 3.1 컴플라이언트 모드

컴플라이언트 모드는 모터의 토크를 해제하여 수동으로 움직일 수 있게 합니다.

```python
# 모든 모터를 컴플라이언트 모드로 설정
reachy.neck.turn_off()

print("이제 로봇의 목을 손으로 움직일 수 있습니다.")
time.sleep(5)

# 모터 다시 활성화
reachy.neck.turn_on()
```

### 3.2 개별 모터 제어

```python
# 특정 모터만 컴플라이언트 모드로
reachy.neck.pitch.compliant = True

print("pitch 모터만 수동으로 움직일 수 있습니다.")
time.sleep(3)

# 다시 활성화
reachy.neck.pitch.compliant = False
```

### 3.3 모터 상태 확인

```python
# 모터 정보 출력
print(f"Pitch - 컴플라이언트: {reachy.neck.pitch.compliant}")
print(f"Pitch - 현재 위치: {reachy.neck.pitch.present_position:.2f}도")
print(f"Pitch - 목표 위치: {reachy.neck.pitch.goal_position:.2f}도")
print(f"Pitch - 현재 속도: {reachy.neck.pitch.present_speed:.2f}도/s")
print(f"Pitch - 부하: {reachy.neck.pitch.present_load:.2f}%")
print(f"Pitch - 온도: {reachy.neck.pitch.temperature}°C")
```

### 3.4 안전한 모터 관리

```python
def safe_motor_control():
    """안전하게 모터를 제어하는 예제"""
    try:
        # 모터 활성화
        reachy.neck.turn_on()

        # 동작 수행
        reachy.neck.goto(
            goal_positions={'pitch': 20, 'yaw': 15},
            duration=2.0
        )

    except Exception as e:
        print(f"오류 발생: {e}")

    finally:
        # 항상 컴플라이언트 모드로 종료
        reachy.neck.turn_off()
        print("모터 안전하게 종료됨")

safe_motor_control()
```

### 3.5 모터 온도 모니터링

```python
import time

def monitor_temperature(duration=10):
    """모터 온도를 주기적으로 확인"""
    start_time = time.time()

    while time.time() - start_time < duration:
        temp = reachy.neck.pitch.temperature
        print(f"모터 온도: {temp}°C")

        # 온도가 너무 높으면 경고
        if temp > 60:
            print("⚠️ 경고: 모터 온도가 높습니다!")
            reachy.neck.turn_off()
            break

        time.sleep(1)

monitor_temperature(duration=10)
```

---

## 4. 과제(test3.py)
- 원형 궤적을 따라 머리를 움직이는 프로그램 작성
- 중력 보상 모드에서 머리를 움직였을 때의 동작 분석

```python
import math
import time
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose
 

with ReachyMini() as mini:
    """부드러운 원형 궤적 데모"""
    mini.enable_gravity_compensation()

    try:
        # 원형 패턴으로 움직이기
        num_points = 40
        radius = 20  # mm
        duration_per_point = 0.2

        for i in range(num_points):
            angle = 4 * 2 * math.pi * i / num_points
            x = radius * math.cos(angle)    # x축 반지름
            y = radius * math.sin(angle)

            mini.goto_target(
                head=create_head_pose(x=x, y=y, mm=True),
                duration=duration_per_point,
                method='minjerk'
            )

        # 원래 위치로 복귀
        mini.goto_target(
            head=create_head_pose(pitch=0, yaw=0, mm=True),
            duration=1.0
        )
    finally:
        mini.disable_gravity_compensation()
```

![](week3_test3.mp4)