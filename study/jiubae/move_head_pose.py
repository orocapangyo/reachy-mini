import logging

from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

logging.getLogger().setLevel(logging.ERROR)
mini = ReachyMini(media_backend="no_media", log_level="ERROR")
try:
    # 머리를 왼쪽으로 이동 (y축 -10mm)
    pose = create_head_pose(y=-10, mm=True)
    mini.goto_target(head=pose, duration=2.0)

    # 초기 위치로 복귀
    pose = create_head_pose()
    mini.goto_target(head=pose, duration=2.0)

    # 머리를 위로 들고(z축) 롤(roll) 회전
    pose = create_head_pose(z=10, roll=15, degrees=True, mm=True)
    mini.goto_target(head=pose, duration=2.0)

    # 초기 위치로 복귀
    pose = create_head_pose()
    mini.goto_target(head=pose, duration=2.0)
finally:
    mini.client.disconnect()
