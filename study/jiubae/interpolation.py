import logging
import time

import numpy as np
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose


logging.getLogger().setLevel(logging.ERROR)


def compare_interpolation_methods(mini: ReachyMini) -> None:
    """linear, minjerk, cartoon, ease 보간 방법 비교."""
    methods = ["linear", "minjerk", "cartoon", "ease_in_out"]
    print("\n[1] 보간 방법 비교")
    for method in methods:
        print(f"- 방법: {method}")
        mini.goto_target(
            head=create_head_pose(y=10, mm=True),
            duration=2.0,
            method=method,
        )
        time.sleep(0.5)
        mini.goto_target(
            head=create_head_pose(),
            duration=2.0,
            method=method,
        )
        time.sleep(0.5)


def realtime_sine_tracking(mini: ReachyMini, run_seconds: float = 5.0) -> None:
    """사인파 궤적을 실시간으로 추종."""
    print("\n[2] 실시간 동작 제어 (사인파 추종)")
    mini.set_target(head=create_head_pose())
    start = time.time()
    while True:
        t = time.time() - start
        if t > run_seconds:
            break
        y = 10.0 * np.sin(2.0 * np.pi * 0.5 * t)
        mini.set_target(head=create_head_pose(y=float(y), mm=True))
        time.sleep(0.01)
    mini.goto_target(head=create_head_pose(), duration=1.0)


def motor_control_demo(mini: ReachyMini) -> None:
    """모터 활성화/컴플라이언스/비활성화 예제."""
    print("\n[3] 모터 제어")
    try:
        mini.enable_motors()
        print("- 모터 활성화 완료")
        time.sleep(1.0)

        mini.make_motors_compliant()
        print("- 컴플라이언스 모드 전환 완료")
        time.sleep(1.0)

        mini.disable_motors()
        print("- 모터 비활성화 완료")
    except Exception as exc:
        # 시뮬레이터/모델별 지원 차이를 고려해 전체 실행은 계속한다.
        print(f"- 모터 제어 데모 건너뜀: {exc}")


def safety_range_test(mini: ReachyMini) -> None:
    """안전 범위를 벗어난 명령 시 클램핑 동작 확인."""
    print("\n[4] 안전 범위 테스트")
    pose = create_head_pose(roll=-50, degrees=True)
    mini.goto_target(head=pose, duration=1.5)
    current_pose = mini.get_current_head_pose()
    print(f"- 현재 머리 포즈: {current_pose}")


def main() -> None:
    mini = ReachyMini(media_backend="no_media", log_level="ERROR")
    try:
        print("Reachy Mini 연결 성공")
        compare_interpolation_methods(mini)
        realtime_sine_tracking(mini, run_seconds=5.0)
        motor_control_demo(mini)
        safety_range_test(mini)
        print("\n모든 실습 항목 완료")
    finally:
        mini.client.disconnect()


if __name__ == "__main__":
    main()