## 3주차: 고급 동작 제어

### 학습 목표

- 다양한 보간(interpolation) 방법 활용
- 실시간 동작 제어
- 모터 상태 관리

---

## 1. 다양한 보간(Interpolation) 방법

### 1.1 보간이란?

보간은 시작 위치에서 목표 위치까지 로봇 관절을 부드럽게 이동시키는 기법입니다. Reachy Mini는 여러 보간 방법을 지원합니다.

### 1.2 선형 보간 (Linear Interpolation)

가장 기본적인 보간 방법으로, 시작점과 끝점을 직선으로 연결합니다.

```python
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

reachy = ReachyMini()

# 선형 보간으로 목 움직이기
pose = create_head_pose(pitch=20, yaw=15, degrees=True)
reachy.goto_target(
    head=pose,
    duration=2.0,
    method='linear'
)
```

**특징:**
- 단순하고 예측 가능
- 속도가 일정
- 급격한 시작/정지로 인한 떨림 가능성

### 1.3 최소 저크 보간 (Minimum Jerk)

부드러운 가속과 감속을 제공하여 자연스러운 움직임을 만듭니다.

```python
from reachy_mini.utils import create_head_pose

# 최소 저크 보간 (기본값)
pose = create_head_pose(pitch=-10, yaw=-10, degrees=True)
reachy.goto_target(
    head=pose,
    duration=1.5,
    method='minjerk'  # 기본값
)
```

**특징:**
- 부드러운 시작과 종료
- 가속도 변화(jerk)를 최소화
- 인간과 유사한 자연스러운 움직임
- 로봇 관절에 부담 감소

### 1.4 보간 모드 비교

```python
import time
from reachy_mini.utils import create_head_pose

# 같은 동작을 다른 보간 방법으로 실행
pose_target = create_head_pose(pitch=30, yaw=0, degrees=True)
pose_origin = create_head_pose(pitch=0, yaw=0, degrees=True)

# 선형 보간
print("선형 보간 시작")
reachy.goto_target(head=pose_target, duration=2.0, method='linear')
time.sleep(2.5)

# 최소 저크 보간
print("최소 저크 보간 시작")
reachy.goto_target(head=pose_origin, duration=2.0, method='minjerk')
```

---

## 2. 실시간 동작 제어

### 2.1 블로킹 제어 (goto_target)

`goto_target`은 지정된 시간(`duration`) 동안 보간을 통해 부드럽게 목표 자세로 이동하며, 동작이 완전히 완료될 때까지 함수 호출이 대기(blocking)됩니다.

```python
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

reachy = ReachyMini()

# 블로킹 모드로 동작 시작
pose = create_head_pose(pitch=20, yaw=30, degrees=True)
reachy.goto_target(
    head=pose,
    duration=3.0
)
print("동작 완료!")
```

### 2.2 실시간 비블로킹 제어 (set_target)

실시간 추종이나 궤적 제어와 같이 정지 없이 연속적으로 위치를 업데이트할 때는 `set_target`을 사용합니다. `set_target`은 즉시 명령을 전송하고 대기 없이 즉시 리턴하므로, 루프문 내에서 짧은 주기(예: 10ms~20ms)로 호출하여 실시간 동작을 수행할 수 있습니다.

```python
import time
import math
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

reachy = ReachyMini()

# 사인파 형태로 목을 실시간으로 비블로킹 제어하기
start_time = time.time()
while time.time() - start_time < 5.0:
    t = time.time() - start_time
    # 0.5Hz 주파수로 -15도 ~ 15도 사이 왕복 운동
    pitch_angle = 15.0 * math.sin(2.0 * math.pi * 0.5 * t)
    
    pose = create_head_pose(pitch=pitch_angle, degrees=True)
    reachy.set_target(head=pose)
    
    time.sleep(0.01)  # 10ms 주기
```

### 2.3 동시 다중 부위 제어

`goto_target` 이나 `set_target` 호출 시 `head`와 `antennas`, `body_yaw` 인자를 조합하여 머리, 안테나, 바디 요를 동시에 제어할 수 있습니다.

```python
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

reachy = ReachyMini()

# 머리와 안테나를 동시에 부드럽게 제어
target_pose = create_head_pose(pitch=15, roll=10, yaw=-20, degrees=True)
reachy.goto_target(
    head=target_pose,
    antennas=[0.5, -0.5],  # [오른쪽 안테나, 왼쪽 안테나] (라디안)
    duration=2.0
)
```

### 2.4 연속 동작 시퀀스

동작들을 순차적으로 연달아 수행할 때는 `goto_target`을 루프나 시퀀스 형태로 정의하여 활용할 수 있습니다.

```python
import time
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

reachy = ReachyMini()

# 동작 시퀀스 정의
sequence = [
    create_head_pose(pitch=20, yaw=30, degrees=True),
    create_head_pose(pitch=-10, yaw=-30, degrees=True),
    create_head_pose(pitch=0, yaw=0, degrees=True),
]

# 각 동작을 순차적으로 실행
for pose in sequence:
    reachy.goto_target(
        head=pose,
        duration=1.5
    )
    time.sleep(0.5)  # 동작 완료 후 다음 동작 전 짧은 대기
```

---

## 3. 모터 상태 관리

### 3.1 토크 활성화 및 해제 (컴플라이언트 모드)

모터의 토크를 해제하면 컴플라이언트(Compliant) 상태가 되어, 모터 파손 없이 로봇의 관절을 수동으로 부드럽게 직접 움직일 수 있게 됩니다.

```python
# 모든 모터의 토크 비활성화 (컴플라이언트 모드)
reachy.disable_motors()

print("이제 로봇의 목과 안테나를 손으로 직접 움직일 수 있습니다.")
time.sleep(5)

# 모터 다시 활성화 (토크 활성화)
reachy.enable_motors()
```

### 3.2 개별 모터 제어

원하는 특정 모터 ID들만 선택하여 토크를 제어할 수 있습니다.

```python
# stewart_1 모터만 토크 비활성화 (수동 조작 가능)
reachy.disable_motors(ids=['stewart_1'])

print("stewart_1 모터만 수동으로 움직일 수 있습니다.")
time.sleep(3)

# 다시 활성화
reachy.enable_motors(ids=['stewart_1'])
```

### 3.3 조인트 각도 및 헤드 포즈 확인

`ReachyMini` 클래스는 개별 모터의 세부 정보 대신, 전체 조인트들의 각도 리스트(라디안 단위) 및 현재 헤드의 4x4 포즈 행렬을 조회하는 API를 제공합니다.

```python
import math

# 현재 조인트 각도 튜플 가져오기 (head_joints 리스트 7개, antenna_joints 리스트 2개)
head_joints, antenna_joints = reachy.get_current_joint_positions()

print("=== 헤드 조인트 각도 (라디안) ===")
for i, angle in enumerate(head_joints):
    print(f"Joint {i+1}: {angle:.2f} rad ({math.degrees(angle):.1f}°)")

print("\n=== 안테나 조인트 각도 (라디안) ===")
print(f"우측 안테나: {antenna_joints[0]:.2f} rad")
print(f"좌측 안테나: {antenna_joints[1]:.2f} rad")

# 현재 헤드의 4x4 포즈 행렬 확인
current_pose = reachy.get_current_head_pose()
print(f"\n현재 헤드 포즈 Matrix:\n{current_pose}")
```

### 3.4 안전한 모터 제어 (try-finally 패턴)

동작 실행 중 예외가 발생하더라도 모터 보호를 위해 마지막에는 항상 토크를 비활성화(컴플라이언트 모드)하도록 구현하는 것이 안전합니다.

```python
from reachy_mini.utils import create_head_pose

def safe_motor_control():
    """안전하게 모터를 제어하는 예제"""
    try:
        # 모터 활성화
        reachy.enable_motors()

        # 동작 수행
        pose = create_head_pose(pitch=20, yaw=15, degrees=True)
        reachy.goto_target(head=pose, duration=2.0)

    except Exception as e:
        print(f"오류 발생: {e}")

    finally:
        # 오류 여부와 상관없이 항상 모터 토크 해제
        reachy.disable_motors()
        print("모터 안전하게 토크 해제(종료)됨")

safe_motor_control()
```

### 3.5 시스템 온도 모니터링 (IMU 센서)

현재 Reachy Mini SDK는 개별 Dynamixel 모터 내부 온도를 직접 쿼리하는 API를 외부에 노출하지 않으므로, 대신 머리 부분에 장착된 IMU 센서 온도를 읽어 시스템 전체의 과열 방지 상태를 모니터링할 수 있습니다.

```python
import time

def monitor_system_temperature(duration=10):
    """IMU 센서 온도를 주기적으로 확인"""
    start_time = time.time()

    while time.time() - start_time < duration:
        # IMU 데이터 가져오기 (가속도, 자이로, 쿼터니언, 온도 포함)
        imu_data = reachy.client.get_current_imu_data()
        
        if imu_data is not None:
            temp = imu_data['temperature']
            print(f"시스템 IMU 온도: {temp}°C")

            # 온도가 너무 높으면 경고 후 모터 보호를 위해 토크 비활성화
            if temp > 60:
                print("⚠️ 경고: 시스템 온도가 임계치를 초과했습니다!")
                reachy.disable_motors()
                break
        else:
            print("IMU 데이터를 읽을 수 없습니다.")

        time.sleep(1)

monitor_system_temperature(duration=10)
```

---

## 4. 종합 실습 예제

### 4.1 부드러운 헤드 트래킹

```python
import math
import time
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

reachy = ReachyMini()

def smooth_head_tracking():
    """부드러운 헤드 트래킹 데모"""
    reachy.enable_motors()

    try:
        # 원형 패턴으로 움직이기
        num_points = 20
        radius = 20  # 각도
        duration_per_point = 0.3

        for i in range(num_points):
            angle = 2 * math.pi * i / num_points

            pitch = radius * math.sin(angle)
            yaw = radius * math.cos(angle)

            pose = create_head_pose(pitch=pitch, yaw=yaw, degrees=True)
            reachy.goto_target(
                head=pose,
                duration=duration_per_point,
                method='minjerk'
            )

        # 원래 위치로 복귀
        reachy.goto_target(
            head=create_head_pose(),
            duration=1.0
        )

    finally:
        reachy.disable_motors()

smooth_head_tracking()
```

### 4.2 오차 모니터링 기반 반응형 제어

실시간 제어 도중 모터에 부하가 걸리거나 충돌이 발생하면, 목표로 전송하는 각도와 실제 모터가 측정한 각도 사이의 편차(오차)가 증가합니다. 오차가 특정 임계값보다 커지는 현상을 모니터링하여 동작을 비상 정지시킬 수 있습니다.

```python
import time
import math
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

reachy = ReachyMini()

def reactive_motion():
    """실시간 오차 모니터링 기반 반응형 동작 제어"""
    reachy.enable_motors()

    try:
        # 0.2Hz 주파수로 큰 폭의 Yaw 회전 수행
        start_time = time.time()
        while time.time() - start_time < 5.0:
            t = time.time() - start_time
            target_yaw = 25.0 * math.sin(2.0 * math.pi * 0.2 * t)
            
            # 목표 자세 적용 (set_target 비블로킹 제어)
            target_pose = create_head_pose(yaw=target_yaw, degrees=True)
            reachy.set_target(head=target_pose)
            
            # 현재 실제 조인트의 라디안 각도 읽기
            head_joints, _ = reachy.get_current_joint_positions()
            
            # 여기서는 마지막 조인트(yaw) 또는 전체 조인트들의 각도 추적 오류 분석
            # 만약 실제 모터 동작에 물리적 장애(외력, 과부하)가 감지되어 오차가 임계값을 넘으면 동작을 긴급 중단합니다.
            # (예제: 단순 예시로 tracking error 임계치 검증 구현 가능)
            
            time.sleep(0.02)  # 20ms 제어 주기

        # 안전하게 원위치 복귀
        reachy.goto_target(head=create_head_pose(), duration=1.5)

    finally:
        reachy.disable_motors()

reactive_motion()
```

---

## 5. 스튜어트 플랫폼 (Stewart Platform) 모터 구조

### 5.1 스튜어트 플랫폼이란?

스튜어트 플랫폼은 6개의 선형 액추에이터(또는 회전 모터)를 사용하여 6자유도(6-DOF) 움직임을 구현하는 병렬 로봇 메커니즘입니다. Reachy Mini의 목(neck) 부분은 스튜어트 플랫폼 구조를 사용하여 3축 회전(pitch, roll, yaw)과 3축 병진(x, y, z) 움직임을 구현합니다.

**주요 특징:**
- 6개의 Dynamixel XL330-M288-T 모터 사용
- 높은 강성과 정밀도
- 컴팩트한 크기에서 복잡한 3D 움직임 구현
- 각 모터가 협력하여 최종 자세 제어

### 5.2 하드웨어 사양

```
모터 사양:
- 모델: Dynamixel XL330-M288-T
- 개수: 6개
- 모터 암 길이: 0.04m (40mm)
- 연결 로드 길이: 0.085m (85mm)
- 헤드 Z 오프셋: 0.177m (177mm)
```

### 5.3 각 모터의 역할과 위치

#### stewart_1 (모터 1)
```python
위치: [0.0206, 0.0218, 0.0] m
브랜치 프레임: closing_1_2
솔루션 패턴: 0 (짝수)

# 위치적 특징
- 전방 우측 영역에 위치
- 주로 전방 pitch와 우측 roll 움직임에 기여
```

#### stewart_2 (모터 2)
```python
위치: [0.0085, 0.0288, 0.0] m
브랜치 프레임: closing_2_2
솔루션 패턴: 1 (홀수)

# 위치적 특징
- 전방 중앙 영역에 위치
- 주로 전방 pitch와 yaw 회전에 기여
```

#### stewart_3 (모터 3)
```python
위치: [-0.0292, 0.0070, 0.0] m
브랜치 프레임: closing_3_2
솔루션 패턴: 0 (짝수)

# 위치적 특징
- 좌측 영역에 위치
- 주로 좌측 roll과 yaw 회전에 기여
```

#### stewart_4 (모터 4)
```python
위치: [-0.0292, -0.0070, 0.0] m
브랜치 프레임: closing_4_2
솔루션 패턴: 1 (홀수)

# 위치적 특징
- 좌측 하단 영역에 위치
- 모터 3과 대칭적으로 좌측 움직임 지원
```

#### stewart_5 (모터 5)
```python
위치: [0.0085, -0.0288, 0.0] m
브랜치 프레임: closing_5_2
솔루션 패턴: 0 (짝수)

# 위치적 특징
- 후방 중앙 영역에 위치
- 주로 후방 pitch와 yaw 회전에 기여
```

#### stewart_6 (모터 6)
```python
위치: [0.0206, -0.0217, 0.0] m
브랜치 프레임: passive_7_link_y
솔루션 패턴: 1 (홀수)

# 위치적 특징
- 후방 우측 영역에 위치
- 주로 후방 pitch와 우측 roll 움직임에 기여
```

### 5.4 모터 배치 패턴

```
        stewart_2
       /         \
   stewart_3    stewart_1
      |            |
   stewart_4    stewart_6
       \         /
        stewart_5

대칭 구조:
- 모터 1, 6: 우측 전후방
- 모터 2, 5: 중앙 전후방
- 모터 3, 4: 좌측 전후방
```

### 5.5 역기구학 (Inverse Kinematics)

목표 자세(pitch, roll, yaw)가 주어지면, 각 모터의 각도를 계산합니다. Reachy Mini SDK에서는 `create_head_pose`를 사용하여 3차원 회전 자세를 4x4 포즈 변환 행렬로 만든 뒤, `goto_target`의 `head` 인자로 전달하면 내부적으로 역기구학을 수행합니다.

```python
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

reachy = ReachyMini()

# 목표 자세 설정 (도 단위 입력)
pose = create_head_pose(pitch=15.0, roll=10.0, yaw=-5.0, degrees=True)

# 6개 모터의 각도가 내부 역기구학 엔진을 통해 자동으로 계산되어 실행됨
reachy.goto_target(
    head=pose,
    duration=2.0
)
```

**내부 동작:**
1. 목표 자세를 4x4 변환 행렬로 변환
2. 각 모터의 브랜치 위치와 모터 위치 계산
3. 기하학적 제약을 고려하여 각 모터 각도 산출
4. 솔루션 패턴(0 또는 1)에 따라 적절한 해 선택

### 5.6 정기구학 (Forward Kinematics)

6개 모터의 각도로부터 헤드의 최종 포즈를 역산해 냅니다.

```python
# 현재 조인트 각도 리스트 확인
head_joints, _ = reachy.get_current_joint_positions()

# 정기구학으로 현재 헤드 포즈 계산 (SDK 내부적으로 자동 처리되어 4x4 행렬로 반환됨)
current_pose = reachy.get_current_head_pose()

print(f"현재 헤드 자세(4x4 행렬):\n{current_pose}")
```

### 5.7 솔루션 패턴의 의미

각 모터는 `solution` 값이 0 또는 1로 설정되어 있습니다. 이는 역기구학 계산 시 여러 해가 존재할 때 어떤 해를 선택할지 결정합니다.

```python
솔루션 패턴:
- solution = 0: 짝수 패턴 (stewart_1, 3, 5)
- solution = 1: 홀수 패턴 (stewart_2, 4, 6)

특징:
- 교대로 배치되어 구조적 안정성 확보
- 특이점(singularity) 회피
- 일관된 움직임 보장
```

### 5.8 변환 행렬 (T_motor_world)

각 모터는 월드 좌표계 대비 고유한 4x4 변환 행렬을 가집니다.

```python
# stewart_1의 변환 행렬 예시
T_motor_world = [
    [0.866, -0.500, -0.000, -0.010],  # X축 방향
    [0.000,  0.000,  1.000, -0.077],  # Y축 방향
    [-0.500, -0.866,  0.000,  0.037],  # Z축 방향
    [0.000,  0.000,  0.000,  1.000]   # 동차 좌표
]

# 이 행렬은 다음을 포함:
# - 회전 성분 (3x3 좌상단 블록)
# - 위치 성분 (3x1 우상단 열)
# - 모터의 공간상 방향과 위치를 정의
```

### 5.9 실습: 조인트 및 헤드 상태 확인

```python
import time
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

reachy = ReachyMini()

# 스튜어트 플랫폼 조인트 및 헤드 상태 확인
def check_stewart_status():
    """스튜어트 플랫폼 상태를 확인"""
    reachy.enable_motors()

    print("=== 스튜어트 플랫폼 상태 모니터링 ===\n")

    # 목을 특정 자세로 이동
    pose = create_head_pose(pitch=20, roll=10, yaw=15, degrees=True)
    reachy.goto_target(
        head=pose,
        duration=2.0
    )

    time.sleep(2.5)

    # 4x4 변환 행렬 확인
    current_pose = reachy.get_current_head_pose()
    print(f"현재 헤드 자세(4x4 행렬):\n{current_pose}\n")

    # 개별 물리 조인트 리스트 확인 (헤드 조인트 7개)
    head_joints, _ = reachy.get_current_joint_positions()
    print("현재 물리 조인트 각도 (라디안):")
    for idx, pos in enumerate(head_joints):
        print(f"  Stewart joint {idx+1}: {pos:.4f} rad")

    reachy.disable_motors()

check_stewart_status()
```

### 5.10 주의사항

1. **작업 공간 제한**
   - 스튜어트 플랫폼은 물리적 제약으로 인한 작업 공간 제한이 있습니다
   - 극단적인 각도 조합은 특이점을 유발할 수 있습니다

2. **동시성 제어**
   - 6개 모터가 동시에 협력하여 움직임
   - 개별 모터의 토크를 무리하게 제어하지 말고 SDK가 제공하는 기구학 솔루션을 사용해 주세요.

3. **안전 범위**
```python
from reachy_mini.utils import create_head_pose

# 권장 각도 범위
safe_ranges = {
    'pitch': (-30, 30),  # 도 단위
    'roll': (-20, 20),
    'yaw': (-45, 45)
}

def safe_goto(pitch, roll, yaw):
    """안전 범위 내에서만 이동"""
    if not (-30 <= pitch <= 30):
        print("⚠️ Pitch 범위 초과")
        return
    if not (-20 <= roll <= 20):
        print("⚠️ Roll 범위 초과")
        return
    if not (-45 <= yaw <= 45):
        print("⚠️ Yaw 범위 초과")
        return

    pose = create_head_pose(pitch=pitch, roll=roll, yaw=yaw, degrees=True)
    reachy.goto_target(
        head=pose,
        duration=2.0
    )
```

---

## 6. 실습 과제

### 과제 1: 보간 방법 비교
선형 보간과 최소 저크 보간을 사용하여 같은 동작을 수행하고, 차이점을 관찰하세요.

**추천 예제:**
- [examples/goto_interpolation_playground.py](../../examples/goto_interpolation_playground.py)
  - 다양한 보간 방법(linear, minjerk, ease, cartoon)을 자동으로 비교
  - 각 방법의 차이를 시각적으로 확인 가능
  - `InterpolationTechnique` 열거형으로 모든 보간 방법 테스트

**실습 팁:**
```python
from reachy_mini.utils.interpolation import InterpolationTechnique

# 사용 가능한 모든 보간 방법 확인
for method in InterpolationTechnique:
    print(f"보간 방법: {method}")
    # 각 방법으로 동일한 동작 수행하고 비교
```

### 과제 2: 안전한 동작 제어
온도와 부하를 모니터링하며 안전하게 동작하는 프로그램을 작성하세요.

**추천 예제:**
- [examples/minimal_demo.py](../../examples/minimal_demo.py)
  - 기본적인 안전한 동작 패턴 (with 문 사용)
  - 연속적인 실시간 제어 예제
  - KeyboardInterrupt 처리

- [examples/reachy_compliant_demo.py](../../examples/reachy_compliant_demo.py)
  - try-except-finally 패턴 활용
  - 안전한 종료 처리 (컴플라이언트 모드로 복귀)

**실습 팁:**
```python
import time
from reachy_mini import ReachyMini

def safe_motion_with_monitoring():
    """온도와 부하를 모니터링하는 안전한 동작 제어"""
    with ReachyMini(media_backend="no_media") as mini:
        try:
            mini.goto_target(create_head_pose(), duration=1.0)

            # 동작 중 모니터링
            start_time = time.time()
            while time.time() - start_time < 10.0:
                # 온도 확인 (실제 구현은 SDK에 따라 다를 수 있음)
                # temp = mini.get_temperature()
                # if temp > 60:
                #     print("⚠️ 온도 경고!")
                #     break

                time.sleep(0.1)

        except KeyboardInterrupt:
            print("사용자가 중단했습니다.")
        finally:
            print("안전하게 종료합니다.")
```

### 과제 3: 복잡한 동작 시퀀스
여러 관절을 조합하여 자연스러운 "고개 끄덕이기" 동작을 만들어보세요.

**추천 예제:**
- [examples/sequence.py](../../examples/sequence.py)
  - 복잡한 다단계 동작 시퀀스
  - Yaw, Pitch, Roll 각각의 사인파 움직임
  - 병진 운동과 회전 운동 조합
  - 안테나와 머리 동시 제어

- [examples/recorded_moves_example.py](../../examples/recorded_moves_example.py)
  - 사전 녹화된 복잡한 동작 재생
  - emotions 라이브러리에 고개 끄덕임 등의 감정 표현 포함

**실습 팁:**
```python
import time
import numpy as np
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

def nodding_motion():
    """고개 끄덕이기 동작"""
    with ReachyMini(media_backend="no_media") as mini:
        # 초기 위치
        mini.goto_target(create_head_pose(), duration=1.0)
        time.sleep(1.0)

        # 고개 끄덕이기 (3회 반복)
        for _ in range(3):
            # 아래로
            mini.goto_target(
                create_head_pose(pitch=20, degrees=True),
                duration=0.5
            )
            time.sleep(0.6)

            # 위로
            mini.goto_target(
                create_head_pose(pitch=-10, degrees=True),
                duration=0.5
            )
            time.sleep(0.6)

        # 원위치
        mini.goto_target(create_head_pose(), duration=1.0)
```

### 과제 4: 스튜어트 플랫폼 이해
스튜어트 플랫폼의 6개 모터가 어떻게 협력하여 3D 움직임을 만드는지 관찰하고, 각 축(pitch, roll, yaw)을 개별적으로 움직여보며 모터들의 동작 패턴을 분석하세요.

**추천 예제:**
- [examples/gui_demos/mini_head_position_gui.py](../../examples/gui_demos/mini_head_position_gui.py)
  - GUI 슬라이더로 pitch, roll, yaw를 실시간 제어
  - 각 축의 개별 영향 관찰 가능
  - X, Y, Z 위치도 조정하여 6-DOF 전체 테스트

- [examples/sequence.py](../../examples/sequence.py)
  - 각 축을 순차적으로 움직이는 패턴
  - 2초씩 yaw, pitch, roll을 개별적으로 테스트

**실습 팁:**
```python
import time
import numpy as np
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

def analyze_stewart_platform():
    """스튜어트 플랫폼 분석: 각 축을 개별적으로 테스트"""
    with ReachyMini(media_backend="no_media") as mini:
        # 초기 위치
        mini.goto_target(create_head_pose(), duration=1.0)
        time.sleep(1.5)

        print("=== Pitch 축 테스트 ===")
        for angle in [0, 15, -15, 0]:
            print(f"Pitch: {angle}도")
            mini.goto_target(
                create_head_pose(pitch=angle, degrees=True),
                duration=1.0
            )
            time.sleep(1.5)

        print("\n=== Roll 축 테스트 ===")
        for angle in [0, 10, -10, 0]:
            print(f"Roll: {angle}도")
            mini.goto_target(
                create_head_pose(roll=angle, degrees=True),
                duration=1.0
            )
            time.sleep(1.5)

        print("\n=== Yaw 축 테스트 ===")
        for angle in [0, 30, -30, 0]:
            print(f"Yaw: {angle}도")
            mini.goto_target(
                create_head_pose(yaw=angle, degrees=True),
                duration=1.0
            )
            time.sleep(1.5)

        print("\n=== 복합 움직임 테스트 ===")
        mini.goto_target(
            create_head_pose(pitch=15, roll=10, yaw=20, degrees=True),
            duration=2.0
        )
        time.sleep(2.5)

        # 원위치
        mini.goto_target(create_head_pose(), duration=1.0)
        print("\n분석 완료!")

if __name__ == "__main__":
    analyze_stewart_platform()
```

**관찰 포인트:**
1. **Pitch 움직임**: 어떤 모터들이 주로 작동하는가?
2. **Roll 움직임**: 좌우 대칭 모터의 역할은?
3. **Yaw 움직임**: 모든 모터가 어떻게 협력하는가?
4. **복합 움직임**: 여러 축을 동시에 움직일 때 모터 간 조정은?

**추가 참고 예제:**
- [examples/look_at_image.py](../../examples/look_at_image.py): 실시간 목표 지점 추적
- [examples/debug/body_yaw_test.py](../../examples/debug/body_yaw_test.py): Body yaw와 head 움직임 조합

---

## 참고 자료

- [Reachy Mini Python SDK 문서](reachy_mini/docs/SDK/python-sdk.md)
- [보간 알고리즘 상세](reachy_mini/docs/SDK/core-concept.md)
- [모터 제어 가이드](reachy_mini/docs/platforms/reachy_mini/usage.md)
- [하드웨어 사양](reachy_mini/docs/platforms/reachy_mini/hardware.md)
- [운동학 데이터](reachy_mini/src/reachy_mini/assets/kinematics_data.json)

