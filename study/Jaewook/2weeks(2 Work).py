import numpy as np
import time
from reachy_mini import ReachyMini

def express_joy(mini):
    """기쁨: 안테나를 빠르게 위아래로"""
    for _ in range(3):
        mini.goto_target(antennas=np.deg2rad([60, 60]), duration=0.3)
        mini.goto_target(antennas=np.deg2rad([30, 30]), duration=0.3)
    mini.goto_target(antennas=[0, 0], duration=1.0)

def express_sadness(mini):
    """슬픔: 안테나를 천천히 내리기"""
    mini.goto_target(antennas=np.deg2rad([10, 10]), duration=3.0)
    time.sleep(2)
    mini.goto_target(antennas=[0, 0], duration=2.0)

def express_surprise(mini):
    """놀람: 안테나를 갑자기 펼치기"""
    mini.goto_target(antennas=[0, 0], duration=0.1)
    time.sleep(0.5)
    mini.goto_target(antennas=np.deg2rad([80, 80]), duration=0.2)
    time.sleep(1)
    mini.goto_target(antennas=[0, 0], duration=1.5)

def express_curiosity(mini):
    """호기심: 안테나를 번갈아 움직이기"""
    for _ in range(2):
        mini.goto_target(antennas=np.deg2rad([45, 0]), duration=0.5)
        mini.goto_target(antennas=np.deg2rad([0, 45]), duration=0.5)
    mini.goto_target(antennas=[0, 0], duration=1.0)

def express_anger(mini):
    """화남: 안테나를 빠르고 강하게 움직이기"""
    for _ in range(4):
        mini.goto_target(antennas=np.deg2rad([70, 70]), duration=0.2)
        mini.goto_target(antennas=np.deg2rad([20, 20]), duration=0.2)
    mini.goto_target(antennas=[0, 0], duration=1.0)

# 사용 예시
with ReachyMini() as mini:
    print("기쁨 표현")
    express_joy(mini)
    time.sleep(1)

    print("슬픔 표현")
    express_sadness(mini)
    time.sleep(1)

    print("놀람 표현")
    express_surprise(mini)
    time.sleep(1)

    print("호기심 표현")
    express_curiosity(mini)
    time.sleep(1)

    print("화남 표현")
    express_anger(mini)