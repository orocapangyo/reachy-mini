리치미니 모터 테스트
```
import time
import numpy as np
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

def run_comprehensive_test():
    with ReachyMini() as mini:
        print("=== [1] 보간 방법(Interpolation) 비교 테스트 ===")
        # linear: 직선적, minjerk: 부드러움, cartoon: 튕기는 느낌, ease: 서서히 가속/감속
        methods = ["linear", "minjerk", "cartoon", "ease_in_out"]

        for method in methods:
            print(f"현재 방법: {method} - 움직임을 관찰하세요.")
            # 목표 지점으로 이동
            mini.goto_target(
                head=create_head_pose(y=10, mm=True),
                duration=1.5,
                method=method
            )
            time.sleep(0.5)
            # 원점으로 복귀
            mini.goto_target(head=create_head_pose(), duration=1.5, method=method)
            time.sleep(0.5)

        input("\n엔터를 누르면 [2] 실시간 제어 테스트를 시작합니다...")

        print("\n=== [2] 실시간 동작 제어 (Sine Wave) ===")
        print("10초 동안 부드럽게 좌우(Yaw)로 흔듭니다.")
        mini.goto_target(head=create_head_pose(), duration=1.0)
        start = time.time()

        while True:
            t = time.time() - start
            if t > 10: break

            # y = A * sin(2 * pi * f * t)
            # 10mm 진폭으로 0.5Hz 주파수(2초에 한 번 왕복) 운동
            y_pos = 10 * np.sin(2 * np.pi * 0.5 * t)
            
            # set_target은 goto_target과 달리 대기하지 않고 즉시 명령을 보냅니다.
            mini.set_target(head=create_head_pose(y=y_pos, mm=True))
            time.sleep(0.01) # 100Hz 주기로 업데이트

        mini.enable_motors()

        input("\n엔터를 누르면 [3] 모터 제어(컴플라이언스) 테스트를 시작합니다...")
        mini.disable_motors()
        mini.compliant = True
        
        print("\n=== [3] 모터 제어 테스트 (중력 보상) ===")
        print("지금부터 5초간 로봇 머리가 '흐물흐물'해집니다. 손으로 직접 움직여보세요!")
        
        for i in range(10, 0, -1):
            print(f"{i}초 남음...")
            time.sleep(1)
            
        print("모터를 다시 잠급니다(stiff).")
        mini.enable_motors()
        mini.goto_target(head=create_head_pose(), duration=1.0)

        input("\n엔터를 누르면 [4] 안전 범위 테스트를 시작합니다...")

        print("\n=== [4] 안전 범위 테스트 ===")
        # Roll 제한은 보통 -40~40도입니다. -50도를 입력해봅니다.
        print("제한 범위(-40도)를 벗어나는 -50도 회전을 시도합니다.")
        excessive_pose = create_head_pose(roll=-50, degrees=True)
        mini.goto_target(head=excessive_pose, duration=1.5)

        # 실제 도달한 위치 확인 (로봇이 스스로 제한한 값을 확인 가능)
        current_pose = mini.get_current_head_pose()
        print(f"명령값: -50도 | 실제 도달 포즈: {current_pose}")

        print("\n모든 테스트가 완료되었습니다. 초기 위치로 복귀합니다.")
        mini.goto_target(head=create_head_pose(), antennas=[0, 0], duration=2.0)

if __name__ == "__main__":
    run_comprehensive_test()
```

# 1. 원형 궤적
```
import numpy as np
import time
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

def move_circle_trajectory(robot, duration=5.0, radius=15, frequency=0.5):
    """
    radius: 원의 크기 (도 단위)
    frequency: 초당 회전 수 (0.5면 2초에 한 바퀴)
    """
    start_time = time.time()
    print(f"{duration}초 동안 원형 궤적 운동을 시작합니다.")

    while (time.time() - start_time) < duration:
        t = time.time() - start_time
        
        # 원형 궤적 공식: x = cos(t), y = sin(t)
        # 같은 주파수(frequency)를 사용해야 찌그러지지 않은 원이 됩니다.
        roll = radius * np.cos(2 * np.pi * frequency * t)
        pitch = radius * np.sin(2 * np.pi * frequency * t)
        
        # 실시간 제어를 위해 set_target 사용
        robot.set_target(head=create_head_pose(roll=roll, pitch=pitch))
        
        # 시뮬레이션 주기 동기화 (100Hz)
        time.sleep(0.01)

with ReachyMini() as mini:
    # 원형 궤적 실행
    move_circle_trajectory(mini, duration=6.0, radius=20, frequency=0.5)
    
    # 종료 후 정면 복귀
    mini.goto_target(head=create_head_pose(), duration=1.0)
```

https://github.com/user-attachments/assets/50dccc04-4a44-46cf-b437-c0af1e22455e



# 2. 중력 보상

## 1. 제어 원리
역동학(Inverse Dynamics)의 활용중력 보상 모드에서는 로봇의 질량 중심(Center of Mass)을 기반으로 각 관절에 가해지는 중력 토크(tau_g)를 실시간으로 계산합니다.<br/>
<img width="276" height="49" alt="image" src="https://github.com/user-attachments/assets/ff061990-8897-4d71-8f04-488019c50f73" /><br/>
여기서 G(q) 항(중력)만을 모터가 보상해주기 때문에, 사용자는 로봇의 무게를 느끼지 않고 조작할 수 있습니다.<br/>

## 2. 동작 분석 (예상 결과)
Stiff 모드: 마우스로 끌면 원래 위치로 돌아가려는 복원력이 발생함. (스프링 효과)<br/>
Compliant 모드: 마우스로 움직이는 대로 이동하며, 외력을 제거하면 그 자리에 정지해 있음. (무중력 효과)<br/>

## 3. 분석 결론
중력 보상 모드는 로봇을 외부 힘에 순응(Compliance)하게 만듭니다. <br/>
이는 사람이 로봇을 직접 잡고 동작을 가르치는 수동 교시(Kinesthetic Teaching)의 핵심 기술이며, 충돌 시 로봇과 사람의 안전을 보장하는 장치가 됩니다.

## Placo 설치하기
```
# 가상 환경이 활성화된 상태에서 입력하세요
pip install placo
```

## 데몬을 실행 (에러 발생해서 좀 더 봐야할 것 같습니다)
```
.\reachy-mini-daemon --sim --deactivate-audio --kinematics-engine Placo
```

## 코드
```
import time

from reachy_mini import ReachyMini

print(
    "This demo currently only works with Placo as the kinematics engine. Start the daemon with:\nreachy-mini-daemon --kinematics-engine Placo"
)
with ReachyMini(media_backend="no_media") as mini:
    try:
        mini.disable_motors()
        mini.compliant = True

        print("Reachy Mini is now compliant. Press Ctrl+C to exit.")
        while True:
            # do nothing, just keep the program running
            time.sleep(0.02)
    except KeyboardInterrupt:
        pass
    finally:
        mini.enable_motors()
        mini.compliant = False
        print("Exiting... Reachy Mini is stiff again.")
```
