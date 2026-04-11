"""
스피커 출력 학습

리치 미니의 스피커를 사용하여:
1. 단순 톤 재생
2. 멜로디 생성 및 재생
3. 상황별 피드백음
4. 음성 레벨 조절

사용법:
    python 02_speaker_output.py --mode <mode> --duration <seconds>

    mode:
      - melody: 멜로디 (도레미파솔라시도) 재생
      - feedback: 상황별 피드백음
"""

import argparse
import numpy as np
import time
import sys

try:
    from reachy_mini.media.media_manager import MediaManager, MediaBackend
except ImportError:
    print("Error: reachy_mini 패키지가 필요합니다.")
    print("설치: pip install reachy-mini")
    sys.exit(1)

from audio_synthesizer import AudioSynthesizer


def play_audio(audio: MediaManager, waveform, sample_rate):
    """
    오디오 데이터 재생

    Args:
        audio: MediaManager 인스턴스
        waveform: numpy 배열 (1D 또는 2D)
        sample_rate: 샘플링 레이트
    """
    channels = audio.get_output_channels()

    # 채널에 맞게 변환
    if waveform.ndim == 1:
        if channels == 2:
            # 모노 → 스테레오
            waveform = np.stack([waveform, waveform], axis=1)
        else:
            # 모노 유지
            waveform = waveform[:, np.newaxis]

    waveform = waveform.astype(np.float32)

    # 재생
    audio.start_playing()
    try:
        audio.push_audio_sample(waveform)
        duration = waveform.shape[0] / sample_rate
        time.sleep(duration + 0.1)  # 약간의 버퍼
    finally:
        audio.stop_playing()

def demo_melody(audio: MediaManager, synthesizer: AudioSynthesizer):
    """
    멜로디 재생 (도레미파솔라시도)
    """
    print("\n멜로디 재생 시작...")
    print("도레미파솔라시도를 재생합니다.\n")

    sample_rate = audio.get_output_audio_samplerate()

    # 도레미파솔라시도
    notes = [
        ('C', 4, 0.4),  # Do
        ('D', 4, 0.4),  # Re
        ('E', 4, 0.4),  # Mi
        ('F', 4, 0.4),  # Fa
        ('G', 4, 0.4),  # Sol
        ('A', 4, 0.4),  # La
        ('B', 4, 0.4),  # Si
        ('C', 5, 0.8),  # Do (높음)
    ]

    all_tones = []

    for note, octave, duration in notes:
        freq = AudioSynthesizer.note_to_frequency(note, octave)

        # 톤 생성
        tone = synthesizer.generate_tone(freq, duration, amplitude=0.2)
        tone = synthesizer.apply_fade(tone, fade_duration=0.03)

        all_tones.append(tone)

        print(f"  {note}{octave} ({freq:.1f} Hz)")

    # 모든 톤 연결
    full_melody = synthesizer.concatenate_signals(*all_tones)

    print(f"\n총 길이: {len(full_melody) / sample_rate:.2f}초")
    print("재생 중...\n")

    # 재생
    play_audio(audio, full_melody, sample_rate)

    print("✓ 완료!")


def demo_feedback(audio: MediaManager, synthesizer: AudioSynthesizer):
    """
    상황별 피드백음 재생
    """
    print("\n피드백음 재생 시작 (12초)...")

    sample_rate = audio.get_output_audio_samplerate()

    feedback_patterns = {
        "success": {
            "description": "작업 성공",
            "notes": [
                (1000, 0.15),
                (1200, 0.15),
            ],
        },
        "error": {
            "description": "오류 발생",
            "notes": [
                (400, 0.2),
                (300, 0.2),
            ],
        },
        "warning": {
            "description": "경고",
            "notes": [
                (800, 0.12),
                (800, 0.12),
                (800, 0.12),
            ],
        },
        "question": {
            "description": "확인 필요",
            "notes": [
                (600, 0.3),
            ],
        },
    }

    for feedback_type, pattern in feedback_patterns.items():
        print(f"\n{feedback_type}: {pattern['description']}")

        all_tones = []

        for freq, duration in pattern["notes"]:
            # 톤 생성
            tone = synthesizer.generate_tone(freq, duration, amplitude=0.25)
            tone = synthesizer.apply_fade(tone, fade_duration=0.02)
            all_tones.append(tone)

        # 간격 추가
        silence = synthesizer.add_silence(0.1)
        all_tones.append(silence)

        # 연결 및 재생
        full_sound = synthesizer.concatenate_signals(*all_tones)
        print(f"  재생 중... ({len(full_sound) / sample_rate:.2f}초)")
        play_audio(audio, full_sound, sample_rate)

    print("\n✓ 완료!")

def main():
    parser = argparse.ArgumentParser(
        description="리치 미니 스피커 출력 처리 학습"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="tone",
        choices=["melody", "feedback"],
        help="실행 모드",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=5,
        help="실행 시간 (초)",
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("스피커 출력 처리 학습")
    print("=" * 60)

    # 오디오 장치 초기화
    try:
        print("\n오디오 장치 초기화 중...")
        audio = MediaManager(backend=MediaBackend.DEFAULT_NO_VIDEO)
        sample_rate = audio.get_output_audio_samplerate()
        channels = audio.get_output_channels()

        print(f"✓ 샘플링 레이트: {sample_rate} Hz")
        print(f"✓ 출력 채널: {channels}")
        print(f"✓ 실행 모드: {args.mode}\n")

    except Exception as e:
        print(f"\n✗ 오류: 오디오 장치를 초기화할 수 없습니다.")
        print(f"상세: {e}")
        print("\n💡 해결 방법:")
        print("1. reachy_mini 패키지 설치 확인:")
        print("   pip install reachy-mini")
        sys.exit(1)

    # 합성기 생성
    synthesizer = AudioSynthesizer(sample_rate=sample_rate)

    try:
        # 선택된 모드 실행
        if args.mode == "melody":
            demo_melody(audio, synthesizer)
        elif args.mode == "feedback":
            demo_feedback(audio, synthesizer)
            
    except KeyboardInterrupt:
        print("\n\n프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"\n✗ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
