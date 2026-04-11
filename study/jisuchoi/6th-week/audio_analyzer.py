#!/usr/bin/env python3
"""
오디오 신호 분석 유틸리티

리치 미니의 마이크 신호를 분석하기 위한 도구 클래스를 제공합니다.
"""

import numpy as np


class AudioAnalyzer:
    """
    오디오 신호 분석 클래스

    RMS, dB, 진폭, ZCR, FFT 등 다양한 신호 분석 기능을 제공합니다.

    속성:
        audio: SoundDeviceAudio 인스턴스
        sample_rate: 샘플링 레이트 (Hz)

    예제:
        >>> from audio_analyzer import AudioAnalyzer
        >>> from reachy_mini.media.audio_sounddevice import SoundDeviceAudio
        >>> audio = SoundDeviceAudio()
        >>> analyzer = AudioAnalyzer(audio)
        >>> sample = audio.get_audio_sample()
        >>> rms = analyzer.calculate_rms(sample)
        >>> db = analyzer.calculate_db(rms)
    """

    def __init__(self, audio):
        """
        AudioAnalyzer 초기화

        Args:
            audio: SoundDeviceAudio 또는 ReSpeakerAudio 인스턴스
        """
        self.audio = audio
        self.sample_rate = audio.get_input_audio_samplerate()

    def calculate_rms(self, sample):
        """
        RMS (Root Mean Square) 계산

        신호의 에너지를 나타냅니다.

        Args:
            sample: numpy 배열 (shape: (num_samples, num_channels))

        Returns:
            float: RMS 값 (0 ~ 1)

        공식:
            RMS = √(Σ(x²) / N)
        """
        return np.sqrt(np.mean(sample ** 2))

    def calculate_db(self, rms):
        """
        dB (데시벨) 변환

        RMS를 상대적인 크기로 표현합니다.

        Args:
            rms: RMS 값

        Returns:
            float: dB 값 (-∞ ~ 0)

        공식:
            dB = 20 × log₁₀(RMS)
        """
        return 20 * np.log10(rms + 1e-10)

    def calculate_amplitude(self, sample):
        """
        진폭 (Amplitude) 계산

        신호의 최대값을 반환합니다.

        Args:
            sample: numpy 배열

        Returns:
            float: 진폭 값 (0 ~ 1)
        """
        return np.max(np.abs(sample))

    def calculate_zcr(self, sample):
        """
        영점 교차율 (Zero Crossing Rate) 계산

        신호가 0을 지나가는 횟수를 세어 음성의 음색 정보를 나타냅니다.

        Args:
            sample: 1D numpy 배열 (채널 크기: len(sample))

        Returns:
            float: ZCR 값 (0 ~ 1)

        해석:
            - 높은 ZCR: 음성 모음(a, e, i) 또는 노이즈
            - 낮은 ZCR: 음성 자음(p, t, k) 또는 조용한 구간

        공식:
            ZCR = (부호 변화 수) / (2 × 샘플 수)
        """
        sign_changes = np.sum(np.abs(np.diff(np.sign(sample))))
        zcr = sign_changes / (2 * len(sample))
        return zcr

    def analyze_spectrum(self, sample):
        """
        주파수 분석 (FFT: Fast Fourier Transform)

        시간 영역의 신호를 주파수 영역으로 변환하여 주요 주파수를 찾습니다.

        Args:
            sample: numpy 배열 (shape: (num_samples, num_channels))

        Returns:
            tuple: (peak_freq, peak_energy)
                - peak_freq: 가장 강한 주파수 (Hz)
                - peak_energy: 해당 주파수의 에너지

        주파수 범위:
            - 음성 기본음(F0): 80-250 Hz (남성), 150-300 Hz (여성)
            - 음성 배음: 250-4000 Hz
        """
        # FFT 계산 (첫 번째 채널만 사용)
        fft = np.abs(np.fft.fft(sample[:, 0]))
        frequencies = np.fft.fftfreq(len(sample), 1 / self.sample_rate)

        # 양수 주파수만 추출
        positive_idx = frequencies > 0
        fft = fft[positive_idx]
        frequencies = frequencies[positive_idx]

        # 피크 주파수 찾기
        peak_idx = np.argmax(fft)
        peak_freq = frequencies[peak_idx]

        return peak_freq, fft[peak_idx]

    def analyze_frequency_bands(self, sample):
        """
        주파수 대역별 에너지 분석

        신호를 3개의 주파수 대역으로 나누어 각 대역의 에너지 비율을 계산합니다.

        Args:
            sample: numpy 배열 (shape: (num_samples, num_channels))

        Returns:
            dict: 주파수 대역별 에너지 비율
                - 'low': 저주파 (0-500 Hz) 비율
                - 'speech': 음성 대역 (500-2000 Hz) 비율
                - 'high': 고주파 (2000-4000 Hz) 비율

        대역 정의:
            - 0-500 Hz: 배경 노이즈, 저주파 진동
            - 500-2000 Hz: 음성의 기본음 및 초기 배음 (가장 중요)
            - 2000-4000 Hz: 음성의 고주파 배음 (명확성)
        """
        # FFT 계산
        fft = np.abs(np.fft.fft(sample[:, 0]))
        frequencies = np.fft.fftfreq(len(sample), 1 / self.sample_rate)

        # 양수 주파수만 추출
        positive_idx = frequencies > 0
        fft = fft[positive_idx]
        frequencies = frequencies[positive_idx]

        # 대역별 에너지 계산
        low = np.sum(fft[(frequencies > 0) & (frequencies < 500)])
        speech = np.sum(fft[(frequencies >= 500) & (frequencies < 2000)])
        high = np.sum(fft[(frequencies >= 2000) & (frequencies < 4000)])

        total = low + speech + high

        return {
            'low': low / total if total > 0 else 0,      # 저주파 비율
            'speech': speech / total if total > 0 else 0,  # 음성 비율
            'high': high / total if total > 0 else 0,      # 고주파 비율
        }

    def is_speech(self, rms, threshold=0.05):
        """
        음성/침묵 판별 (간단한 에너지 기반)

        RMS 값이 임계값을 초과하면 음성으로 판별합니다.

        Args:
            rms: RMS 값
            threshold: 음성 감지 임계값 (기본값: 0.05)

        Returns:
            bool: 음성 여부

        주의:
            이는 매우 간단한 방법입니다. 더 정확한 감지는 다음을 고려할 수 있습니다:
            - 시간 기반 필터링 (연속 여러 프레임 판정)
            - ZCR 통합 (노이즈 vs 음성 구분)
            - 스펙트럼 분석 (음성 대역 에너지)
        """
        return rms > threshold

    def record_audio(self, duration_seconds=5, show_progress=True):
        """
        마이크에서 음성 녹음

        Args:
            duration_seconds: 녹음 시간 (초)
            show_progress: 진행 상황 표시 여부

        Returns:
            tuple: (recorded_audio, sample_rate)
                - recorded_audio: 1D numpy 배열 (float32)
                - sample_rate: 샘플링 레이트 (Hz)
        """
        import time

        print(f"\n녹음 시작... ({duration_seconds}초)")
        if show_progress:
            print("음성을 입력하세요.")

        self.audio.start_recording()

        try:
            sample_rate = self.sample_rate
            all_samples = []

            samples_needed = int(sample_rate * duration_seconds)
            start_time = time.time()

            while samples_needed > 0:
                sample = self.audio.get_audio_sample()
                if sample is not None:
                    # 첫 번째 채널만 사용 (모노)
                    all_samples.append(sample[:, 0])
                    samples_needed -= sample.shape[0]

                    # 진행 상황 표시
                    if show_progress:
                        elapsed = time.time() - start_time
                        progress = min(elapsed / duration_seconds * 100, 100)
                        bar_length = 30
                        filled = int(bar_length * progress / 100)
                        bar = "█" * filled + "░" * (bar_length - filled)
                        print(f"\r[{bar}] {progress:.0f}% ({elapsed:.1f}s/{duration_seconds}s)",
                              end="", flush=True)

            recorded_audio = np.concatenate(all_samples)

            if show_progress:
                print("\n✓ 녹음 완료")

            return recorded_audio, sample_rate

        except KeyboardInterrupt:
            print("\n✗ 녹음 중단됨")
            return None, None
        finally:
            self.audio.stop_recording()

    def save_wav(self, audio_data, filename="temp_audio.wav"):
        """
        음성 데이터를 WAV 파일로 저장

        Args:
            audio_data: numpy 배열 (float32)
            filename: 저장할 파일명

        Returns:
            str | None: 저장된 파일 경로, 실패 시 None
        """
        try:
            import scipy.io.wavfile as wavfile
        except ImportError:
            print("Error: scipy 패키지가 필요합니다.")
            print("설치 방법: pip install scipy")
            return None

        try:
            # float32를 int16으로 변환
            audio_int = (audio_data * 32767).astype(np.int16)
            wavfile.write(filename, self.sample_rate, audio_int)
            print(f"✓ 음성 파일 저장: {filename}")
            return filename
        except Exception as e:
            print(f"Error: 파일 저장 실패 - {e}")
            return None
