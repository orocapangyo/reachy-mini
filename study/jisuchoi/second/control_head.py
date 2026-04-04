from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

with ReachyMini() as mini:
    # 머리를 왼쪽으로 이동 (y축 -10mm)
    pose = create_head_pose(y=-10, mm=True)
    mini.goto_target(head=pose, duration=2.0)

    # 초기 위치로 복귀
    pose = create_head_pose()
    mini.goto_target(head=pose, duration=2.0)
