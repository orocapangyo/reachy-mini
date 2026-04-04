#!/usr/bin/env python3
"""
Reachy Mini 동작 녹화 및 재생 데모

이 스크립트는 다음 기능을 제공합니다:
1. 로봇 동작 녹화 (모터 비활성화 후 수동으로 움직이며 녹화)
2. 녹화된 동작 재생
3. Hugging Face Hub에서 동작 라이브러리 다운로드 및 재생

사용 전 시뮬레이션 데몬을 먼저 실행하세요:
    reachy-mini-daemon --sim
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
from reachy_mini import ReachyMini
from reachy_mini.motion.recorded_move import RecordedMove, RecordedMoves


def print_menu():
    """메뉴 출력"""
    print("\n" + "=" * 50)
    print("🤖 Reachy Mini 동작 녹화/재생 데모")
    print("=" * 50)
    print("1. 동작 녹화 (Recording)")
    print("2. 녹화된 동작 재생 (Playback)")
    print("3. Hugging Face Hub 동작 재생")
    print("4. 로봇 Wake Up")
    print("5. 로봇 Sleep")
    print("6. 현재 관절 상태 확인")
    print("0. 종료")
    print("=" * 50)


def record_motion(reachy: ReachyMini, duration: float = 5.0, filename: Optional[str] = None) -> Optional[Path]:
    """
    동작 녹화
    
    Args:
        reachy: ReachyMini 인스턴스
        duration: 녹화 시간 (초)
        filename: 저장할 파일명 (없으면 자동 생성)
    
    Returns:
        저장된 파일 경로 또는 None
    """
    print("\n📹 동작 녹화 모드")
    print("-" * 40)
    
    # 모터 비활성화 (수동 조작 가능하게)
    print("모터를 비활성화합니다... (로봇을 수동으로 움직일 수 있습니다)")
    reachy.disable_motors()
    time.sleep(0.5)
    
    input(f"\n로봇을 원하는 시작 위치로 움직인 후 Enter를 누르세요...")
    
    print(f"\n3초 후 {duration}초 동안 녹화를 시작합니다...")
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    print("🔴 녹화 시작! 로봇을 움직여 주세요.")
    reachy.start_recording()
    
    # 녹화 중 상태 표시
    start_time = time.time()
    while time.time() - start_time < duration:
        remaining = duration - (time.time() - start_time)
        print(f"\r  녹화 중... 남은 시간: {remaining:.1f}초", end="", flush=True)
        time.sleep(0.1)
    
    print("\n🛑 녹화 종료!")
    recorded_data = reachy.stop_recording()
    
    # 모터 다시 활성화
    print("모터를 다시 활성화합니다...")
    reachy.enable_motors()
    
    if not recorded_data:
        print("❌ 녹화된 데이터가 없습니다.")
        return None
    
    # 파일명 생성
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"motion_{timestamp}.json"
    
    # data 디렉토리 생성
    data_dir = Path("data/motions")
    data_dir.mkdir(parents=True, exist_ok=True)
    filepath = data_dir / filename
    
    # 녹화 데이터를 RecordedMove 형식으로 변환
    time_values = [frame["time"] for frame in recorded_data]
    # 시간을 0부터 시작하도록 조정
    t0 = time_values[0]
    time_values = [t - t0 for t in time_values]
    
    move_data = {
        "description": f"Recorded motion at {datetime.now().isoformat()}",
        "time": time_values,
        "set_target_data": []
    }
    
    for frame in recorded_data:
        set_target = {
            "head": frame.get("head", np.eye(4).tolist()),
            "antennas": frame.get("antennas", [0.0, 0.0]),
            "body_yaw": frame.get("body_yaw", 0.0)
        }
        move_data["set_target_data"].append(set_target)
    
    # 파일 저장
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(move_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 녹화 완료!")
    print(f"   파일: {filepath}")
    print(f"   프레임 수: {len(recorded_data)}")
    print(f"   녹화 시간: {time_values[-1]:.2f}초")
    
    return filepath


def playback_motion(reachy: ReachyMini, filepath: Optional[Path] = None):
    """
    녹화된 동작 재생
    
    Args:
        reachy: ReachyMini 인스턴스
        filepath: 재생할 파일 경로 (없으면 선택)
    """
    print("\n▶️ 동작 재생 모드")
    print("-" * 40)
    
    # 파일 선택
    if filepath is None:
        data_dir = Path("data/motions")
        if not data_dir.exists():
            print("❌ 녹화된 동작이 없습니다. 먼저 녹화를 진행해주세요.")
            return
        
        motion_files = list(data_dir.glob("*.json"))
        if not motion_files:
            print("❌ 녹화된 동작이 없습니다. 먼저 녹화를 진행해주세요.")
            return
        
        print("\n저장된 동작 목록:")
        for i, f in enumerate(motion_files, 1):
            print(f"  {i}. {f.name}")
        
        try:
            choice = int(input("\n재생할 동작 번호를 선택하세요: ")) - 1
            if 0 <= choice < len(motion_files):
                filepath = motion_files[choice]
            else:
                print("❌ 잘못된 선택입니다.")
                return
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
            return
    
    # 파일 로드
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            move_data = json.load(f)
    except Exception as e:
        print(f"❌ 파일 로드 실패: {e}")
        return
    
    # RecordedMove 객체 생성
    move = RecordedMove(move_data)
    
    print(f"\n📁 파일: {filepath.name}")
    print(f"   설명: {move.description}")
    print(f"   길이: {move.duration:.2f}초")
    
    input("\nEnter를 눌러 재생을 시작합니다...")
    
    print("▶️ 재생 시작!")
    reachy.play_move(move, initial_goto_duration=1.0)
    print("✅ 재생 완료!")


def play_from_huggingface(reachy: ReachyMini):
    """
    Hugging Face Hub에서 동작 다운로드 및 재생
    
    Args:
        reachy: ReachyMini 인스턴스
    """
    print("\n🤗 Hugging Face Hub 동작 재생")
    print("-" * 40)
    
    # 기본 데이터셋
    default_dataset = "pollen-robotics/reachy-mini-emotions"
    
    print(f"기본 데이터셋: {default_dataset}")
    dataset_input = input("다른 데이터셋을 사용하려면 입력하세요 (Enter: 기본값): ").strip()
    
    dataset_name = dataset_input if dataset_input else default_dataset
    
    try:
        print(f"\n📥 '{dataset_name}' 다운로드 중...")
        recorded_moves = RecordedMoves(dataset_name)
        
        # 사용 가능한 동작 목록 표시
        available_moves = recorded_moves.list_moves()
        print(f"\n사용 가능한 동작 ({len(available_moves)}개):")
        for i, move_name in enumerate(available_moves, 1):
            print(f"  {i}. {move_name}")
        
        try:
            choice = int(input("\n재생할 동작 번호를 선택하세요: ")) - 1
            if 0 <= choice < len(available_moves):
                selected_move_name = available_moves[choice]
            else:
                print("❌ 잘못된 선택입니다.")
                return
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
            return
        
        # 동작 가져오기
        move = recorded_moves.get(selected_move_name)
        
        print(f"\n📁 동작: {selected_move_name}")
        print(f"   설명: {move.description}")
        print(f"   길이: {move.duration:.2f}초")
        
        input("\nEnter를 눌러 재생을 시작합니다...")
        
        print("▶️ 재생 시작!")
        reachy.play_move(move, initial_goto_duration=1.0, sound=True)
        print("✅ 재생 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")


def show_current_state(reachy: ReachyMini):
    """현재 로봇 상태 표시"""
    print("\n📊 현재 로봇 상태")
    print("-" * 40)
    
    head_joints, antenna_joints = reachy.get_current_joint_positions()
    head_pose = reachy.get_current_head_pose()
    
    print("\n관절 위치 (rad):")
    print(f"  Head:     {[f'{j:.4f}' for j in head_joints]}")
    print(f"  Antennas: {[f'{j:.4f}' for j in antenna_joints]}")
    
    print("\n헤드 포즈 (4x4 matrix):")
    for row in head_pose:
        print(f"  [{', '.join(f'{v:8.4f}' for v in row)}]")


def main():
    """메인 함수"""
    print("\n🚀 Reachy Mini 동작 녹화/재생 데모 시작")
    print("시뮬레이션 데몬에 연결 중...")
    
    try:
        reachy = ReachyMini()
        print("✅ 연결 성공!")
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        print("\n시뮬레이션을 먼저 실행하세요:")
        print("  reachy-mini-daemon --sim")
        return
    
    last_recorded_file = None
    
    try:
        while True:
            print_menu()
            choice = input("선택하세요: ").strip()
            
            if choice == "1":
                # 녹화
                try:
                    duration = float(input("녹화 시간 (초, 기본값 5): ") or "5")
                except ValueError:
                    duration = 5.0
                last_recorded_file = record_motion(reachy, duration=duration)
                
            elif choice == "2":
                # 재생
                playback_motion(reachy, last_recorded_file)
                
            elif choice == "3":
                # HuggingFace Hub 재생
                play_from_huggingface(reachy)
                
            elif choice == "4":
                # Wake up
                print("\n👋 로봇을 깨웁니다...")
                reachy.wake_up()
                print("✅ Wake up 완료!")
                
            elif choice == "5":
                # Sleep
                print("\n😴 로봇을 재웁니다...")
                reachy.goto_sleep()
                print("✅ Sleep 완료!")
                
            elif choice == "6":
                # 상태 확인
                show_current_state(reachy)
                
            elif choice == "0":
                print("\n👋 프로그램을 종료합니다.")
                break
                
            else:
                print("❌ 잘못된 선택입니다. 다시 선택해주세요.")
                
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 중단되었습니다.")
    finally:
        print("로봇 연결을 종료합니다...")


if __name__ == "__main__":
    main()
