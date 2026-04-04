"""8자 패턴으로 머리를 움직이는 프로그램.

daemon이 실행 중인 상태에서 실행:
    python src/jisu_playground/second/assignment_1.py
"""

import time
import math

from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

with ReachyMini() as mini:
    print("8자 패턴 시작 (Ctrl+C로 종료)")

    t0 = time.time()
    dt = 0.02  # 50Hz 업데이트

    try:
        while True:
            t = time.time() - t0
            freq = 0.3  # 8자 한 사이클 ~3.3초

            # 8자 패턴: yaw는 1배 주기, pitch는 2배 주기
            yaw_deg = 25.0 * math.sin(2.0 * math.pi * freq * t)
            pitch_deg = 15.0 * math.sin(4.0 * math.pi * freq * t)

            pose = create_head_pose(yaw=yaw_deg, pitch=pitch_deg, degrees=True)
            mini.set_target(head=pose)

            time.sleep(dt)
    except KeyboardInterrupt:
        print("\n정지. 초기 위치로 복귀합니다.")
        mini.goto_target(head=create_head_pose(), duration=1.0)
