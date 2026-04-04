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
        
        x = 10 * np.sin(2 * np.pi * 0.5 * t)
        y = 10 * np.sin(2 * np.pi * 0.5 * t)

        mini.set_target(head=create_head_pose(y=y, x=x, mm=True))
        time.sleep(0.01)
        
        # 현재 위치 출력
        current_x = mini.get_current_head_pose()[0][3]
        current_y = mini.get_current_head_pose()[1][3]
        current_z = mini.get_current_head_pose()[2][3]
        print(f"Current x: {current_x}, Current y: {current_y}, Current z: {current_z}")
