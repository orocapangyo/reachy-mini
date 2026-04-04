import time
import numpy as np

from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

# 사인파 궤적 추종
with ReachyMini() as mini:
    mini.set_target(head=create_head_pose())
    start = time.time()

    while True:
        t = time.time() - start
        if t > 10:
            break

        y = 10 * np.sin(2 * np.pi * 0.5 * t)
        mini.set_target(head=create_head_pose(y=y, mm=True))
        time.sleep(0.01)
