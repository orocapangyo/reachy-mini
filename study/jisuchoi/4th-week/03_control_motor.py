import time

from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

# ──────────────────────────────────────────────
# 학습 목표
#   1. 모터 생명주기: enable → 작동 → compliant → disable
#   2. 안전 제한(clamping): 범위 초과 명령 시 실제 도달 위치 확인
# ──────────────────────────────────────────────

with ReachyMini() as mini:

    # ── 1단계: 모터 활성화 ──────────────────────
    print("[1] 모터 활성화")
    mini.enable_motors()
    time.sleep(1)

    # 정면으로 이동 (기준 위치 잡기)
    print("    → 정면(원점)으로 이동")
    mini.goto_target(head=create_head_pose())
    time.sleep(1)

    # ── 2단계: 중력 보상 활성화 ─────────────────
    # enable_gravity_compensation: 모터가 중력에 저항하며 현재 자세를 유지
    # → 헤드를 손으로 밀면 저항하지만 무거운 느낌 없이 자세 유지
    # (비활성화하면 중력에 의해 고개가 처짐)
    print("\n[2] 중력 보상 활성화 (3초간)")
    mini.enable_gravity_compensation()
    time.sleep(3)
    mini.disable_gravity_compensation()

    # ── 3단계: 재활성화 후 안전 범위 테스트 ──────
    print("\n[3] 모터 재활성화 → 안전 범위 초과 명령 테스트")
    mini.enable_motors()
    time.sleep(0.5)

    # roll 축 제한: -40 ~ +40도
    # -50도를 명령하면 로봇은 -40도(가장 가까운 유효 위치)로 이동
    target_roll = -50
    print(f"    → 명령 roll: {target_roll}° (제한 범위: -40 ~ +40°)")
    pose = create_head_pose(roll=target_roll, degrees=True)
    mini.goto_target(head=pose)
    time.sleep(1)

    # 실제 도달한 위치 확인 → 명령값과 실제값의 차이 관찰
    current_pose = mini.get_current_head_pose()
    print(f"    → 실제 도달 포즈: {current_pose}")
    print(f"    ※ roll이 {target_roll}°가 아닌 안전 한계값에 고정됨을 확인")
    time.sleep(1)

    # 원점으로 복귀
    print("\n    → 원점 복귀")
    mini.goto_target(head=create_head_pose())
    time.sleep(1)

    # ── 4단계: 모터 비활성화 ────────────────────
    print("\n[4] 모터 비활성화")
    mini.disable_motors()
    print("    완료")
