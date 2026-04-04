from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose
import numpy as np
import time

# 1. 로봇 연결 및 세션 시작
with ReachyMini() as mini:
    print("2주차 제어 및 8자 패턴 실습을 시작합니다!")
    
    # [실습 1] 기본 동작 (생략 가능하지만 확인차 유지)
    mini.goto_target(head=create_head_pose(y=-10, mm=True), duration=1.0)
    time.sleep(0.5)

    # [과제] 8자 패턴 동작 (반드시 with문 내부에 있어야 합니다!)
    print("8자 패턴 시작...")
    for t in np.linspace(0, 2 * np.pi, 25): # 25개 지점으로 정교하게 구성(0 ~ 2π 구간을 25개로 나눔)
        y_val = 15 * np.sin(t)      # 좌우 이동
        z_val = 10 * np.sin(2 * t)  # 상하 이동
       # 8자의 가로/세로 크기 조절
        # 세션이 열려 있는 상태에서 명령 전송
        mini.goto_target(
            head=create_head_pose(y=y_val, z=z_val, mm=True), 
            duration=0.15
        )
        time.sleep(0.05) # 시뮬레이터와 통신 속도 조절

    # [과제] 감정 표현 마무리
    print("놀람 표현 후 종료!")
    mini.goto_target(antennas=np.deg2rad([90, 90]), duration=0.5)
    time.sleep(1)
# 5. 복귀 (핵심 추가 부분)
    print("원래 상태로 복귀")
    mini.goto_target(
        head=create_head_pose(),   # 머리 원위치
        antennas=[0, 0],           # 안테나 원위치
        duration=1.5
    )
    time.sleep(0.5)

print("모든 동작이 완료되었습니다.")