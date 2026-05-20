"""
음성 인식 (STT: Speech-To-Text) 학습

리치 미니의 마이크를 사용하여:
1. 음성 녹음
2. 음성을 텍스트로 변환 (Whisper STT)
3. 텍스트에서 명령 인식 및 로봇 제어

주의: Whisper 모델 다운로드는 처음 실행 시 시간이 걸릴 수 있습니다.
설치: pip install openai-whisper
"""

import argparse
import os
import sys
import time
from pathlib import Path

# 부모 디렉토리(6th-week)를 Python 경로에 추가하여 모듈 import
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from reachy_mini.media.media_manager import MediaManager, MediaBackend
except ImportError:
    print("Error: reachy_mini 패키지가 필요합니다.")
    print("설치: pip install reachy-mini")
    sys.exit(1)

from audio_analyzer import AudioAnalyzer

# Whisper 선택 설치
WHISPER_AVAILABLE = False
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    print("경고: Whisper 모듈이 설치되지 않았습니다.")
    print("음성 인식을 사용하려면: pip install openai-whisper")


def transcribe_audio(audio_file, model_size="base"):
    """
    음성 파일을 텍스트로 변환 (OpenAI Whisper)

    Args:
        audio_file: 음성 파일 경로
        model_size: 모델 크기 (tiny, base, small, medium, large)

    Returns:
        dict | None: 인식 결과 또는 None
    """
    if not WHISPER_AVAILABLE:
        print("Error: Whisper 모듈이 설치되지 않았습니다.")
        print("설치 방법: pip install openai-whisper")
        return None

    try:
        print(f"\n모델 로드 중... ({model_size})")
        model = whisper.load_model(model_size)

        print("음성 인식 중...")
        result = model.transcribe(audio_file, language="ko", fp16=False)

        return result

    except Exception as e:
        print(f"Error: 음성 인식 실패 - {e}")
        return None

def recognize_command(text):
    """
    텍스트에서 명령 인식

    Args:
        text: 인식된 텍스트

    Returns:
        str | None: 명령 타입 또는 None
    """
    commands = {
        "안녕": "greeting",
        "손": "hand",
        "춤": "dance",
        "멈춰": "stop",
        "시간": "time",
    }

    for keyword, command in commands.items():
        if keyword in text.lower():
            return command

    return None

def demo_command_recognition(analyzer, model_size="base", use_sim=False):
    """음성 명령 인식 및 로봇 제어"""
    print("=== 음성 명령 인식 및 로봇 제어 ===")
    print("\n지원하는 명령어:")
    print("  - '안녕': 인사 (wake_up)")
    print("  - '손': 머리(?)를 듦")
    print("  - '춤': 춤 추기")
    print("  - '멈춰': 멈추기 (sleep)")
    print("  - '시간': 현재 시간 출력")
    print()

    # 로봇 초기화 (시뮬레이션 모드)
    mini = None
    if use_sim:
        try:
            print("로봇 초기화 중...")
            from reachy_mini import ReachyMini
            from reachy_mini.utils import create_head_pose
            import numpy as np
            mini = ReachyMini(spawn_daemon=True, use_sim=True)
            print("✓ 시뮬레이션 로봇 준비 완료\n")
        except Exception as e:
            print(f"⚠ 로봇 초기화 실패: {e}")
            print("텍스트 명령만 처리합니다.\n")
            mini = None

    try:
        # 음성 녹음
        audio_data, sample_rate = analyzer.record_audio(duration_seconds=5)

        if audio_data is None:
            return

        # 파일로 저장
        audio_file = analyzer.save_wav(audio_data)

        if audio_file:
            # 음성을 텍스트로 변환
            result = transcribe_audio(audio_file, model_size=model_size)

            if result:
                text = result['text']
                print(f"\n인식된 텍스트: '{text}'")

                # 명령 인식
                command = recognize_command(text)

                if command:
                    print(f"✓ 명령 감지: {command}\n")

                    # 명령 처리
                    if command == "greeting":
                        print("→ 안녕하세요!")
                        if mini:
                            print("→ 로봇이 깨어났습니다!")
                            try:
                                mini.wake_up()
                            except Exception as e:
                                print(f"  (로봇 제어 오류: {e})")

                    elif command == "hand":
                        print("→ 손 동작을 합니다!")
                        if mini:
                            print("→ 로봇이 손을 들었습니다!")
                            try:
                                print("  [디버그] 손 동작 시작...")
                                # 헤드를 위로 향하게 (pitch=-20도 회전)
                                # 리치 미니의 헤드는 위치 이동은 불가능하고 회전만 가능함
                                pose = create_head_pose(pitch=-20, degrees=True)
                                print(f"  [디버그] pose 생성됨: {type(pose)}")
                                mini.set_target(head=pose)
                                time.sleep(1.0)
                                print("  [디버그] 손 동작 완료!")
                            except Exception as e:
                                print(f"  (로봇 제어 오류: {e})")
                                import traceback
                                traceback.print_exc()

                    elif command == "dance":
                        print("→ 춤을 춥니다!")
                        if mini:
                            print("→ 로봇이 춤을 춥니다!")
                            try:
                                print("  [디버그] 춤 동작 시작...")
                                # 격정적인 춤: 리치 미니는 회전만 가능하므로 head의 yaw/pitch로 표현
                                for i in range(5):
                                    print(f"  [디버그] 춤 반복 {i+1}/5")
                                    # 오른쪽으로 회전 (yaw=25도)
                                    pose_right = create_head_pose(yaw=25, degrees=True)
                                    mini.set_target(head=pose_right)
                                    time.sleep(0.3)
                                    # 왼쪽으로 회전 (yaw=-25도)
                                    pose_left = create_head_pose(yaw=-25, degrees=True)
                                    mini.set_target(head=pose_left)
                                    time.sleep(0.3)
                                # 위아래 피치 동작으로도 춤추기
                                for i in range(3):
                                    # 위를 봄 (pitch=-15도)
                                    pose_up = create_head_pose(pitch=-15, degrees=True)
                                    mini.set_target(head=pose_up)
                                    time.sleep(0.25)
                                    # 아래를 봄 (pitch=15도)
                                    pose_down = create_head_pose(pitch=15, degrees=True)
                                    mini.set_target(head=pose_down)
                                    time.sleep(0.25)
                                # 중앙으로 복귀
                                pose_center = create_head_pose()
                                mini.set_target(head=pose_center)
                                print("  [디버그] 춤 동작 완료!")
                            except Exception as e:
                                print(f"  (로봇 제어 오류: {e})")
                                import traceback
                                traceback.print_exc()

                    elif command == "stop":
                        print("→ 멈춥니다!")
                        if mini:
                            print("→ 로봇이 잠들었습니다!")
                            try:
                                mini.goto_sleep()
                            except Exception as e:
                                print(f"  (로봇 제어 오류: {e})")

                    elif command == "time":
                        from datetime import datetime
                        now = datetime.now()
                        time_str = now.strftime("%H:%M:%S")
                        print(f"→ 현재 시간: {time_str}")
                        if mini:
                            try:
                                # 위를 봄 (pitch=-30도)
                                # 리치 미니는 위치 이동은 불가능하고 회전만 가능함
                                pose = create_head_pose(pitch=-30, degrees=True)
                                mini.set_target(head=pose)
                                time.sleep(2)
                                pose_center = create_head_pose()
                                mini.set_target(head=pose_center)
                            except Exception as e:
                                print(f"  (로봇 제어 오류: {e})")

                    elif command == "help":
                        print("→ 도움말을 표시합니다.")
                else:
                    print("✗ 명령을 인식하지 못했습니다.")

            # 임시 파일 삭제
            try:
                os.remove(audio_file)
            except:
                pass

    finally:
        # 로봇 종료
        if mini:
            try:
                mini.close()
            except:
                pass


def main():
    parser = argparse.ArgumentParser(
        description="리치 미니 음성 인식 (STT) 예제"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper 모델 크기"
    )
    parser.add_argument(
        "--sim",
        action="store_true",
        help="시뮬레이션 모드 활성화 (Mujoco 로봇 제어)"
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("음성 인식 (STT: Speech-To-Text) 예제")
    print("=" * 70)

    # 오디오 장치 초기화
    try:
        print("\n오디오 장치 초기화 중...")
        audio = MediaManager(backend=MediaBackend.DEFAULT_NO_VIDEO)
        sample_rate = audio.get_input_audio_samplerate()
        channels = audio.get_input_channels()

        print(f"✓ 샘플링 레이트: {sample_rate} Hz")
        print(f"✓ 입력 채널: {channels}")
        print(f"✓ Whisper 모델: {args.model}")

        if args.sim:
            print(f"✓ 시뮬레이션 모드: 활성화")

        if not WHISPER_AVAILABLE:
            print("✗ Whisper 미설치 - 음성 인식 불가능")

    except Exception as e:
        print(f"\n✗ 오류: 오디오 장치를 초기화할 수 없습니다.")
        print(f"상세: {e}")
        print("\n💡 해결 방법:")
        print("1. reachy_mini 패키지 설치 확인:")
        print("   pip install reachy-mini")
        print("2. Whisper STT 패키지 설치 확인:")
        print("   pip install openai-whisper")
        sys.exit(1)

    # 분석 객체 생성
    analyzer = AudioAnalyzer(audio)

    try:
        print()
        if not WHISPER_AVAILABLE:
            print("Error: Whisper가 설치되지 않아 음성 인식을 실행할 수 없습니다.")
            print("설치: pip install openai-whisper")
            sys.exit(1)

        demo_command_recognition(analyzer, args.model, use_sim=args.sim)

    except KeyboardInterrupt:
        print("\n\n프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"\n✗ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
