import time

from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

methods = ["linear", "minjerk", "cartoon", "ease_in_out"]

def print_menu():
    print("\n--- 보간 방법 선택 ---")
    for i, m in enumerate(methods):
        print(f"  {i}: {m}")
    print("  q: 종료")
    print("----------------------")

with ReachyMini() as mini:
    while True:
        print_menu()
        choice = input("선택 > ").strip()

        if choice == "q":
            print("종료합니다.")
            break

        if not choice.isdigit() or int(choice) not in range(len(methods)):
            print(f"잘못된 입력입니다. 0~{len(methods)-1} 또는 q를 입력하세요.")
            continue

        method = methods[int(choice)]
        print(f"방법: {method}")
        mini.goto_target(
            head=create_head_pose(y=20, mm=True),
            duration=1.0,
            method=method
        )
        time.sleep(1)
        mini.goto_target(head=create_head_pose(), duration=1.0, method=method)
        time.sleep(1)
