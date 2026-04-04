"""안테나로 다양한 감정 표현하기 (기쁨, 슬픔, 놀람 등).

daemon이 실행 중인 상태에서 실행:
    python src/jisu_playground/second/assignment_2.py

안테나 값: [오른쪽, 왼쪽] (라디안)
  양수 → 안쪽으로 접힘, 음수 → 바깥으로 펴짐
"""

import time

from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose


def emotion_happy(mini: ReachyMini):
    """기쁨: 안테나를 빠르게 펄럭이며 고개를 살짝 위로."""
    print("[기쁨] 안테나 펄럭펄럭!")
    mini.goto_target(
        head=create_head_pose(pitch=-5, degrees=True),
        duration=0.3,
    )
    for i in range(6):
        angle = 0.8 if i % 2 == 0 else -0.8
        mini.set_target(antennas=[angle, angle])
        time.sleep(0.15)
    mini.goto_target(head=create_head_pose(), antennas=[0.0, 0.0], duration=0.5)


def emotion_sad(mini: ReachyMini):
    """슬픔: 안테나를 천천히 아래로 축 처지게."""
    print("[슬픔] 안테나가 축 처집니다...")
    mini.goto_target(
        head=create_head_pose(pitch=10, degrees=True),
        antennas=[-0.3, -0.3],
        duration=1.5,
    )
    time.sleep(1.0)
    mini.goto_target(antennas=[-0.6, -0.6], duration=1.0)
    time.sleep(1.0)
    mini.goto_target(head=create_head_pose(), antennas=[0.0, 0.0], duration=1.0)


def emotion_surprise(mini: ReachyMini):
    """놀람: 안테나가 갑자기 쫑긋 서고 고개를 뒤로."""
    print("[놀람] 깜짝!")
    mini.goto_target(
        head=create_head_pose(pitch=-10, degrees=True),
        antennas=[-1.0, 1.0],
        duration=0.2,
    )
    time.sleep(0.8)
    mini.goto_target(head=create_head_pose(), antennas=[0.0, 0.0], duration=0.8)


def emotion_angry(mini: ReachyMini):
    """화남: 안테나를 안쪽으로 접고 고개를 떨며 좌우로."""
    print("[화남] 부들부들...")
    mini.goto_target(antennas=[1.2, 1.2], duration=0.3)
    for _ in range(4):
        mini.goto_target(
            head=create_head_pose(yaw=-8, roll=3, degrees=True),
            duration=0.1,
        )
        mini.goto_target(
            head=create_head_pose(yaw=8, roll=-3, degrees=True),
            duration=0.1,
        )
    mini.goto_target(head=create_head_pose(), antennas=[0.0, 0.0], duration=0.5)


def emotion_curious(mini: ReachyMini):
    """궁금: 고개를 갸웃하며 안테나 한쪽만 세움."""
    print("[궁금] 갸우뚱?")
    mini.goto_target(
        head=create_head_pose(roll=15, yaw=10, degrees=True),
        antennas=[0.8, -0.3],
        duration=0.8,
    )
    time.sleep(1.0)
    mini.goto_target(
        head=create_head_pose(roll=-15, yaw=-10, degrees=True),
        antennas=[-0.3, 0.8],
        duration=0.8,
    )
    time.sleep(1.0)
    mini.goto_target(head=create_head_pose(), antennas=[0.0, 0.0], duration=0.8)


EMOTIONS = {
    "1": ("기쁨", emotion_happy),
    "2": ("슬픔", emotion_sad),
    "3": ("놀람", emotion_surprise),
    "4": ("화남", emotion_angry),
    "5": ("궁금", emotion_curious),
}


with ReachyMini() as mini:
    print("=== 안테나 감정 표현 ===")
    print("번호를 입력하세요 (q: 종료):\n")
    for key, (name, _) in EMOTIONS.items():
        print(f"  {key}. {name}")
    print()

    while True:
        choice = input("> ").strip()
        if choice.lower() == "q":
            print("종료합니다.")
            break
        if choice in EMOTIONS:
            name, func = EMOTIONS[choice]
            func(mini)
            time.sleep(0.3)
        else:
            print("1~5 또는 q를 입력하세요.")
