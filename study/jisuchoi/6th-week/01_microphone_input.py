#!/usr/bin/env python3
"""
마이크 입력 처리 심화 학습

리치 미니의 마이크를 사용하여:
1. 실시간 음성 레벨 모니터링
2. 음성/침묵 구분 (VAD)
3. 주파수 분석 (FFT)
4. 영점 교차율 (ZCR) 계산

사용법:
    python 01_microphone_input.py --mode <mode> --duration <seconds>

    mode:
      - level: 음성 레벨 모니터링
      - speech: 음성/침묵 구분
      - spectrum: 주파수 분석
      - full: 모든 분석을 한 번에
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

from audio_analyzer import AudioAnalyzer


def monitor_audio_level(analyzer, duration_seconds=10):
    """
    실시간 음성 레벨 모니터링

    RMS, dB, 진폭을 실시간으로 표시합니다.
    """
    print(f"\n음성 레벨 모니터링 시작 ({duration_seconds}초)...")
    print("음성을 입력하면 레벨이 표시됩니다.\n")

    analyzer.audio.start_recording()

    try:
        sample_rate = analyzer.sample_rate
        samples_needed = int(sample_rate * duration_seconds)
        total_samples = samples_needed

        while samples_needed > 0:
            sample = analyzer.audio.get_audio_sample()
            if sample is None:
                continue

            # 분석 계산
            rms = analyzer.calculate_rms(sample)
            db = analyzer.calculate_db(rms)
            amplitude = analyzer.calculate_amplitude(sample)
            zcr = analyzer.calculate_zcr(sample[:, 0])

            # 진행 상황
            progress = (total_samples - samples_needed) / total_samples * 100

            # 시각적 막대
            bar_length = 30
            filled = int(bar_length * amplitude)
            bar = "█" * filled + "░" * (bar_length - filled)

            print(f"\r[{bar}] {db:6.1f} dB | RMS: {rms:.4f} | ZCR: {zcr:.4f} | {progress:.0f}%",
                  end="", flush=True)

            samples_needed -= sample.shape[0]

        print("\n\n✓ 완료!")

    except KeyboardInterrupt:
        print("\n\n✗ 중단됨")
    finally:
        analyzer.audio.stop_recording()


def detect_speech(analyzer, threshold=0.05, duration_seconds=15):
    """
    음성/침묵 구분 (VAD - Voice Activity Detection)

    임계값을 기반으로 음성과 침묵을 구분합니다.
    """
    print(f"\n음성/침묵 감지 시작 ({duration_seconds}초)...")
    print(f"임계값: {threshold:.4f}\n")

    analyzer.audio.start_recording()

    try:
        sample_rate = analyzer.sample_rate
        start_time = time.time()
        speech_duration = 0
        silence_duration = 0

        while True:
            elapsed = time.time() - start_time
            if elapsed > duration_seconds:
                break

            sample = analyzer.audio.get_audio_sample()
            if sample is None:
                continue

            # 첫 번째 채널만 사용 (모노)
            single_channel = sample[:, 0]

            # RMS 계산
            rms = analyzer.calculate_rms(single_channel)

            # 음성 여부 판단
            is_speech = analyzer.is_speech(rms, threshold)

            if is_speech:
                speech_duration += sample.shape[0] / sample_rate
                status = "🔴 음성 감지"
                color = "\033[91m"  # 빨강
            else:
                silence_duration += sample.shape[0] / sample_rate
                status = "⚪ 침묵"
                color = "\033[90m"  # 회색

            reset = "\033[0m"

            print(f"\r{color}{status}{reset} | RMS: {rms:.4f} | 진행: {elapsed:.1f}초",
                  end="", flush=True)

        print(f"\n\n=== 결과 ===")
        print(f"음성 시간: {speech_duration:.2f}초")
        print(f"침묵 시간: {silence_duration:.2f}초")
        total = speech_duration + silence_duration
        if total > 0:
            speech_ratio = speech_duration / total * 100
            print(f"음성 비율: {speech_ratio:.1f}%")
            print(f"침묵 비율: {100 - speech_ratio:.1f}%")

    except KeyboardInterrupt:
        print("\n\n✗ 중단됨")
    finally:
        analyzer.audio.stop_recording()


def analyze_spectrum(analyzer: AudioAnalyzer, duration_seconds=5):
    """
    주파수 분석 (FFT)

    음성 신호의 주파수 성분을 분석합니다.
    """
    print(f"\n주파수 분석 시작 ({duration_seconds}초)...")
    print("다양한 음성을 입력하여 주파수 변화를 관찰하세요.\n")

    analyzer.audio.start_recording()

    try:
        sample_rate = analyzer.sample_rate
        samples_needed = int(sample_rate * duration_seconds)
        total_samples = samples_needed

        peak_frequencies = []

        while samples_needed > 0:
            sample = analyzer.audio.get_audio_sample()
            if sample is None:
                continue

            # 스펙트럼 분석
            peak_freq, peak_energy = analyzer.analyze_spectrum(sample)
            peak_frequencies.append(peak_freq)

            # 주파수 대역 분석
            bands = analyzer.analyze_frequency_bands(sample)

            # 진행 상황
            progress = (total_samples - samples_needed) / total_samples * 100

            # 일정 간격으로만 출력 (가독성 향상)
            if int(progress) % 25 == 0 and int(progress) > 0:
                # 시각적 표현
                low_bar = "█" * int(bands['low'] * 20) + "░" * (20 - int(bands['low'] * 20))
                speech_bar = "█" * int(bands['speech'] * 20) + "░" * (20 - int(bands['speech'] * 20))
                high_bar = "█" * int(bands['high'] * 20) + "░" * (20 - int(bands['high'] * 20))

                print(f"주파수: {peak_freq:7.1f} Hz (에너지: {peak_energy:.1f}) | {progress:.0f}%")
                print(f"  저주파 [0-500Hz]     [{low_bar}] {bands['low']*100:5.1f}%")
                print(f"  음성대역 [500-2kHz]  [{speech_bar}] {bands['speech']*100:5.1f}%")
                print(f"  고주파 [2-4kHz]      [{high_bar}] {bands['high']*100:5.1f}%\n")
            else:
                # 진행도만 간단히 표시
                print(f"\r진행 중... {progress:.0f}%", end="", flush=True)

            samples_needed -= sample.shape[0]

        # 통계
        if peak_frequencies:
            avg_freq = np.mean(peak_frequencies)
            std_freq = np.std(peak_frequencies)
            min_freq = np.min(peak_frequencies)
            max_freq = np.max(peak_frequencies)

            print(f"\n\n=== 주파수 통계 ===")
            print(f"평균 주파수: {avg_freq:.1f} Hz")
            print(f"표준편차: {std_freq:.1f} Hz")
            print(f"최소/최대: {min_freq:.1f} ~ {max_freq:.1f} Hz")
            print(f"\n✓ 완료!")

    except KeyboardInterrupt:
        print("\n\n✗ 중단됨")
    finally:
        analyzer.audio.stop_recording()


def full_analysis(analyzer: AudioAnalyzer, threshold=0.05, duration_seconds=20):
    """
    모든 분석을 한 번에 수행

    레벨, VAD, 스펙트럼 정보를 동시에 표시합니다.
    """
    print(f"\n전체 분석 시작 ({duration_seconds}초)...")
    print("다양한 음성을 입력하세요.\n")

    analyzer.audio.start_recording()

    try:
        sample_rate = analyzer.sample_rate
        samples_needed = int(sample_rate * duration_seconds)
        total_samples = samples_needed
        speech_duration = 0

        while samples_needed > 0:
            sample = analyzer.audio.get_audio_sample()
            if sample is None:
                continue

            # 다양한 분석
            single_channel = sample[:, 0]
            rms = analyzer.calculate_rms(single_channel)
            db = analyzer.calculate_db(rms)
            amplitude = analyzer.calculate_amplitude(sample)
            zcr = analyzer.calculate_zcr(single_channel)
            is_speech = analyzer.is_speech(rms, threshold)
            peak_freq, _ = analyzer.analyze_spectrum(sample)
            bands = analyzer.analyze_frequency_bands(sample)

            if is_speech:
                speech_duration += sample.shape[0] / sample_rate

            # 진행 상황
            progress = (total_samples - samples_needed) / total_samples * 100

            # 상세 정보 출력
            status = "🔴 음성" if is_speech else "⚪ 침묵"

            # 진폭 바
            bar_length = 25
            filled = int(bar_length * amplitude)
            bar = "█" * filled + "░" * (bar_length - filled)

            # 음성 대역 에너지 비율을 활용한 음성 판별 신뢰도
            speech_confidence = bands['speech'] * 100

            print(f"\r[{bar}] {status} | {db:6.1f}dB | {peak_freq:7.0f}Hz | ZCR:{zcr:.4f} | Speech:{speech_confidence:5.1f}% | {progress:.0f}%",
                  end="", flush=True)

            samples_needed -= sample.shape[0]

        print(f"\n\n=== 분석 완료 ===")
        print(f"음성 감지 시간: {speech_duration:.2f}초")
        print(f"음성 감지 비율: {speech_duration / duration_seconds * 100:.1f}%")
        print(f"\n✓ 완료!")

    except KeyboardInterrupt:
        print("\n\n✗ 중단됨")
    finally:
        analyzer.audio.stop_recording()


def main():
    parser = argparse.ArgumentParser(
        description="리치 미니 마이크 입력 처리 심화 학습"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="level",
        choices=["level", "speech", "spectrum", "full"],
        help="실행 모드"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=10,
        help="실행 시간 (초)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.05,
        help="음성 감지 임계값"
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("리치 미니 마이크 입력 처리 학습")
    print("=" * 70)

    # 오디오 장치 초기화
    try:
        print("\n오디오 장치 초기화 중...")
        audio = MediaManager(backend=MediaBackend.DEFAULT_NO_VIDEO)
        sample_rate = audio.get_input_audio_samplerate()
        channels = audio.get_input_channels()

        print(f"✓ 샘플링 레이트: {sample_rate} Hz")
        print(f"✓ 입력 채널: {channels}")
        if channels == 4:
            print("✓ ReSpeaker 마이크 배열 감지됨")
        print(f"✓ 실행 모드: {args.mode}")
        print(f"✓ 실행 시간: {args.duration}초")

        if args.mode in ["speech", "full"]:
            print(f"✓ 음성 감지 임계값: {args.threshold}")

    except Exception as e:
        print(f"\n✗ 오류: 오디오 장치를 초기화할 수 없습니다.")
        print(f"상세: {e}")
        print("\n💡 해결 방법:")
        print("1. reachy_mini 패키지 설치 확인:")
        print("   pip install reachy-mini")
        print("2. ReSpeaker 사용 시 드라이버 설치 필요")
        sys.exit(1)

    # 분석 객체 생성
    analyzer = AudioAnalyzer(audio)

    try:
        # 선택된 모드 실행
        if args.mode == "level":
            monitor_audio_level(analyzer, args.duration)
        elif args.mode == "speech":
            detect_speech(analyzer, args.threshold, args.duration)
        elif args.mode == "spectrum":
            analyze_spectrum(analyzer, args.duration)
        elif args.mode == "full":
            full_analysis(analyzer, args.threshold, args.duration)

    except KeyboardInterrupt:
        print("\n\n프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"\n✗ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
