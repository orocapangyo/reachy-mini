import time
import numpy as np
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

# linear, minjerk, cartoon, ease 비교
methods = ["linear", "minjerk", "cartoon", "ease"]

with ReachyMini(media_backend="no_media") as mini:
    mini.goto_target(create_head_pose(), antennas=[0.0, 0.0], duration=1.0)
    try:    
        for method in methods:
            print(f"방법: {method}")
            mini.goto_target(
                head=create_head_pose(y=10, mm=True),
                duration=2.0,
                method=method
            )
            time.sleep(1)
            mini.goto_target(head=create_head_pose(), duration=2.0, method=method)
            time.sleep(1)
    except KeyboardInterrupt:
        pass
