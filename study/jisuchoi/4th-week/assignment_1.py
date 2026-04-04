import time
import numpy as np

from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

RADIUS   = 10.0   # 원 반지름 (단위: 도)
FREQ     = 0.3    # 회전 주파수 (Hz) → 1/0.3 ≈ 3.3초에 한 바퀴
DURATION = 10.0   # 전체 실행 시간 (초)
DT       = 0.01   # 제어 주기 (초) → 100Hz

with ReachyMini() as mini:
    mini.enable_motors()

    # 시작 전 정면으로 복귀
    mini.goto_target(head=create_head_pose(), duration=1.0)
    time.sleep(1.0)

    print("원형 궤적 시작")
    start = time.time()

    while True:
        t = time.time() - start
        if t > DURATION:
            break

        pitch = RADIUS * np.sin(2 * np.pi * FREQ * t)
        yaw   = RADIUS * np.cos(2 * np.pi * FREQ * t)

        mini.set_target(head=create_head_pose(pitch=pitch, yaw=yaw, degrees=True))
        time.sleep(DT)

    print("완료 → 정면 복귀")
    mini.goto_target(head=create_head_pose(), duration=1.0)
    time.sleep(1.0)

    mini.disable_motors()
