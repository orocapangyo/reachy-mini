"""Reachy Mini 동작 녹화/재생 통합 도구.
"""

import argparse
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from reachy_mini import ReachyMini
from reachy_mini.motion.recorded_move import RecordedMove, RecordedMoves
from reachy_mini.utils import create_head_pose


logging.getLogger().setLevel(logging.ERROR)

LIBRARY_DATASETS = {
    "dance": "pollen-robotics/reachy-mini-dances-library",
    "emotions": "pollen-robotics/reachy-mini-emotions-library",
}


def connect_reachy() -> ReachyMini:
    """리치미니 연결"""
    return ReachyMini(media_backend="no_media", log_level="ERROR")


def normalize_recorded_data(recorded_data: list[dict[str, Any]]) -> dict[str, Any]:
    """raw recording을 RecordedMove용 JSON 구조로 변환"""
    if not recorded_data:
        raise ValueError("녹화 데이터가 비어 있습니다.")

    t0 = float(recorded_data[0]["time"])
    time_values = [float(frame["time"]) - t0 for frame in recorded_data]

    set_target_data = []
    for frame in recorded_data:
        set_target_data.append(
            {
                "head": frame.get("head", create_head_pose().tolist()),
                "antennas": frame.get("antennas", [0.0, 0.0]),
                "body_yaw": frame.get("body_yaw", 0.0),
            }
        )

    return {
        "description": f"Recorded at {datetime.now().isoformat()}",
        "time": time_values,
        "set_target_data": set_target_data,
    }


def record_motion(output_path: Path, duration: float, manual: bool) -> Path:
    """녹화 + fallback 처리 + 파일 저장"""
    mini = connect_reachy()
    try:
        print("Reachy Mini 연결 성공")
        print("녹화 시작")
        mini.start_recording()

        fallback_frames: list[dict[str, Any]] = []

        if manual:
            print(f"{duration:.1f}초 동안 로봇을 움직여 주세요.")
            start = time.time()
            sample_dt = 0.05  # 20 Hz 샘플링
            while True:
                now = time.time()
                elapsed = now - start
                if elapsed > duration:
                    break

                try:
                    head_pose = mini.get_current_head_pose().tolist()
                except Exception:
                    head_pose = create_head_pose().tolist()

                try:
                    _, antenna_joints = mini.get_current_joint_positions()
                    antennas = list(antenna_joints)
                except Exception:
                    antennas = [0.0, 0.0]

                fallback_frames.append(
                    {
                        "time": elapsed,
                        "head": head_pose,
                        "antennas": antennas,
                        "body_yaw": 0.0,
                    }
                )
                time.sleep(sample_dt)
        else:
            # 명령 기반 자동 데모 녹화
            demo_poses = [
                create_head_pose(y=10, mm=True),
                create_head_pose(y=-10, mm=True),
                create_head_pose(z=10, roll=10, degrees=True, mm=True),
                create_head_pose(),
            ]
            for idx, pose in enumerate(demo_poses):
                mini.goto_target(head=pose, duration=1.0)
                fallback_frames.append(
                    {
                        "time": float(idx),
                        "head": pose.tolist(),
                        "antennas": [0.0, 0.0],
                        "body_yaw": 0.0,
                    }
                )

        recorded_data = mini.stop_recording()
        if not recorded_data:
            if manual:
                if not fallback_frames:
                    raise RuntimeError(
                        "녹화 데이터가 반환되지 않았고 샘플링 데이터도 없습니다."
                    )
                print("SDK 녹화 데이터가 비어 있어 현재 포즈 샘플링 데이터로 저장합니다.")
                recorded_data = fallback_frames
            else:
                print("녹화 데이터가 비어 있어 명령 시퀀스를 기반으로 파일을 생성합니다.")
                recorded_data = fallback_frames

        payload = normalize_recorded_data(recorded_data)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
        print(f"녹화 저장 완료: {output_path}")
        return output_path
    finally:
        mini.client.disconnect()


def play_motion(input_path: Path) -> None:
    """로컬 JSON 읽어서 재생"""
    if not input_path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {input_path}")

    move_data = json.loads(input_path.read_text())
    move = RecordedMove(move_data)

    mini = connect_reachy()
    try:
        print(f"재생 시작: {input_path}")
        mini.play_move(move, initial_goto_duration=1.0, sound=False)
        print("재생 완료")
    finally:
        mini.client.disconnect()


def play_hf_motion(dataset: str, move_name: str | None) -> None:
    """Play a move from a Hugging Face recorded-moves dataset."""
    print(f"데이터셋 로드 중: {dataset}")
    recorded_moves = RecordedMoves(dataset)
    available_moves = recorded_moves.list_moves()
    if not available_moves:
        raise RuntimeError(f"데이터셋에 재생 가능한 동작이 없습니다: {dataset}")

    selected_move_name = move_name or available_moves[0]
    if selected_move_name not in available_moves:
        raise ValueError(
            f"동작 '{selected_move_name}' 을(를) 찾을 수 없습니다. "
            f"가능한 값: {', '.join(available_moves)}"
        )

    move = recorded_moves.get(selected_move_name)
    mini = connect_reachy()
    try:
        print(f"HF 동작 재생 시작: {selected_move_name}")
        mini.play_move(move, initial_goto_duration=1.0, sound=False)
        print("재생 완료")
    finally:
        mini.client.disconnect()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reachy Mini 동작 녹화/재생 도구")
    sub = parser.add_subparsers(dest="command", required=True)

    record_cmd = sub.add_parser("record", help="동작 녹화 후 JSON 저장")
    record_cmd.add_argument(
        "-o",
        "--output",
        default="recordings/motion.json",
        help="저장 파일 경로 (기본값: recordings/motion.json)",
    )
    record_cmd.add_argument(
        "-d",
        "--duration",
        type=float,
        default=5.0,
        help="수동 녹화 시간(초, manual 모드일 때 사용)",
    )
    record_cmd.add_argument(
        "--manual",
        action="store_true",
        help="명령 데모 대신 수동 움직임을 녹화",
    )

    play_cmd = sub.add_parser("play", help="저장된 JSON 동작 재생")
    play_cmd.add_argument(
        "-i",
        "--input",
        default="recordings/motion.json",
        help="재생할 JSON 파일 경로",
    )

    demo_cmd = sub.add_parser("demo", help="자동 녹화 후 바로 재생")
    demo_cmd.add_argument(
        "-o",
        "--output",
        default="recordings/motion_demo.json",
        help="데모 저장 파일 경로",
    )

    hf_cmd = sub.add_parser("hf-play", help="Hugging Face 데이터셋 동작 재생")
    hf_cmd.add_argument(
        "-l",
        "--library",
        choices=sorted(LIBRARY_DATASETS.keys()),
        default="dance",
        help="기본 라이브러리 선택 (기본값: dance)",
    )
    hf_cmd.add_argument(
        "--dataset",
        type=str,
        help="커스텀 HF dataset id. 지정 시 --library보다 우선",
    )
    hf_cmd.add_argument(
        "-m",
        "--move",
        type=str,
        help="재생할 동작 이름 (미지정 시 첫 번째 동작 재생)",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "record":
        record_motion(Path(args.output), duration=args.duration, manual=args.manual)
    elif args.command == "play":
        play_motion(Path(args.input))
    elif args.command == "demo":
        out = record_motion(Path(args.output), duration=5.0, manual=False)
        play_motion(out)
    elif args.command == "hf-play":
        dataset = args.dataset or LIBRARY_DATASETS[args.library]
        play_hf_motion(dataset=dataset, move_name=args.move)


if __name__ == "__main__":
    main()
