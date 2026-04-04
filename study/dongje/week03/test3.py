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
        radius = 20  # mm
        duration_per_point = 0.2

        for i in range(num_points):
            angle = 4 * 2 * math.pi * i / num_points

            x = radius * math.cos(angle)    # x축 반지름
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