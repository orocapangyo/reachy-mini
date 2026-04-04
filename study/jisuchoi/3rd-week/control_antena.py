import numpy as np

from reachy_mini import ReachyMini

with ReachyMini() as mini:
    # 양쪽 안테나를 45도로 이동
    mini.goto_target(antennas=np.deg2rad([45, 45]), duration=1.0)

    # 초기 위치로 복귀
    mini.goto_target(antennas=[0, 0], duration=1.0)