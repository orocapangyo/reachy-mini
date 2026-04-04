from reachy_mini import ReachyMini, ReachyMiniApp
from reachy_mini.utils import create_head_pose

with ReachyMini() as mini:
    # 머리를 위로 들고(z축) 롤(roll) 회전
    pose = create_head_pose(z=10, roll=15, degrees=True, mm=True)
    mini.goto_target(head=pose, duration=2.0)

