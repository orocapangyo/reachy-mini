#!/usr/bin/env python3
"""
오디오 합성 유틸리티

톤, 멜로디, 신호 생성 및 처리 기능을 제공합니다.
"""

import numpy as np


class AudioSynthesizer:
    """
    오디오 신호 합성 및 생성 클래스

    톤 생성, 멜로디 구성, 페이드 효과, 볼륨 조절 등의 기능을 제공합니다.

    속성:
        sample_rate: 샘플링 레이트 (Hz, 기본값: 16000)

    예제:
        >>> from audio_synthesizer import AudioSynthesizer
        >>> synth = AudioSynthesizer(sample_rate=16000)
        >>> tone = synth.generate_tone(440, 1.0)  # A4, 1초
        >>> tone_with_fade = synth.apply_fade(tone)
    """

    def __init__(self, sample_rate=16000):
        """
        AudioSynthesizer 초기화

        Args:
            sample_rate: 샘플링 레이트 (기본값: 16000 Hz)
        """
        self.sample_rate = sample_rate

    def generate_tone(self, frequency, duration, amplitude=0.3):
        """
        정현파 톤 생성

        톤은 단일 주파수의 정현파 신호입니다.
        음성이나 음악의 기본 요소입니다.

        Args:
            frequency: 주파수 (Hz)
            duration: 지속 시간 (초)
            amplitude: 진폭 (0 ~ 1, 기본값: 0.3)

        Returns:
            numpy 배열 (dtype: float32, shape: (num_samples,))

        공식:
            y(t) = A × sin(2π × f × t)
            - A: 진폭
            - f: 주파수
            - t: 시간
        """
        # 시간 배열 생성
        num_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, num_samples, endpoint=False)

        # 정현파 생성
        tone = amplitude * np.sin(2 * np.pi * frequency * t)

        return tone.astype(np.float32)

    def apply_fade(self, waveform, fade_duration=0.05):
        """
        페이드 인/아웃 효과 적용

        신호의 시작과 끝에 점진적으로 크기를 변화시켜
        클릭 소음을 제거합니다.

        Args:
            waveform: 오디오 신호 (1D numpy 배열)
            fade_duration: 페이드 시간 (초, 기본값: 0.05)

        Returns:
            numpy 배열 (페이드 적용됨)

        효과:
            - 페이드 인: 0 → 1
            - 페이드 아웃: 1 → 0
        """
        # 페이드 샘플 수
        fade_samples = int(self.sample_rate * fade_duration)
        fade_samples = min(fade_samples, len(waveform) // 2)

        # 페이드 곡선 생성
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)

        # 페이드 적용
        waveform = waveform.copy()
        if fade_samples > 0:
            waveform[:fade_samples] *= fade_in
            waveform[-fade_samples:] *= fade_out

        return waveform

    def adjust_volume(self, audio_data, volume_db):
        """
        오디오 데이터의 볼륨을 dB 단위로 조절

        dB는 로그 스케일이므로:
        - +6 dB ≈ 2배 크기
        - -6 dB ≈ 0.5배 크기
        - 0 dB = 원본 볼륨

        Args:
            audio_data: numpy 배열
            volume_db: 볼륨 조절 (dB, -40 ~ +20 범위 권장)

        Returns:
            numpy 배열 (값의 범위: -1 ~ 1로 클리핑됨)

        공식:
            gain = 10^(dB/20)
            result = audio_data × gain
        """
        # dB를 선형 게인으로 변환
        gain = 10 ** (volume_db / 20)

        # 게인 적용
        result = audio_data * gain

        # 오버플로우 방지 (클리핑)
        result = np.clip(result, -1.0, 1.0)

        return result

    def normalize_audio(self, audio_data, target_db=-20):
        """
        음성 레벨을 목표 dB로 정규화

        현재 음성의 RMS를 계산하고 목표 레벨에 맞게 조절합니다.

        Args:
            audio_data: numpy 배열
            target_db: 목표 레벨 (-40 ~ 0, 기본값: -20)

        Returns:
            numpy 배열 (정규화됨)

        주의:
            - 무음 신호(RMS ≈ 0)는 정규화하지 않음
        """
        # 현재 RMS 계산
        rms = np.sqrt(np.mean(audio_data ** 2))

        # 0에 가깝거나 음수 방지
        if rms < 1e-10:
            return audio_data

        current_db = 20 * np.log10(rms)

        # 필요한 게인 계산
        gain_db = target_db - current_db
        gain = 10 ** (gain_db / 20)

        # 정규화
        result = audio_data * gain
        return np.clip(result, -1.0, 1.0)

    def mono_to_stereo(self, mono_signal):
        """
        모노 신호를 스테레오로 변환

        동일한 신호를 두 채널에 복사합니다.

        Args:
            mono_signal: 1D numpy 배열

        Returns:
            2D numpy 배열 (shape: (num_samples, 2))
        """
        stereo = np.stack([mono_signal, mono_signal], axis=1)
        return stereo.astype(np.float32)

    def stereo_to_mono(self, stereo_signal):
        """
        스테레오 신호를 모노로 변환

        좌우 채널을 평균합니다.

        Args:
            stereo_signal: 2D numpy 배열 (shape: (num_samples, 2))

        Returns:
            1D numpy 배열
        """
        if stereo_signal.ndim == 1:
            return stereo_signal

        mono = np.mean(stereo_signal, axis=1)
        return mono.astype(np.float32)

    def concatenate_signals(self, *signals):
        """
        여러 신호를 연결

        Args:
            *signals: 1D numpy 배열들

        Returns:
            연결된 1D numpy 배열
        """
        return np.concatenate(signals).astype(np.float32)

    def mix_signals(self, *signals, normalize=True):
        """
        여러 신호를 혼합 (합산)

        Args:
            *signals: 1D numpy 배열들 (길이가 같아야 함)
            normalize: True일 경우 정규화 (기본값: True)

        Returns:
            혼합된 1D numpy 배열

        주의:
            - 모든 신호는 동일한 길이여야 함
            - normalize=True일 경우 결과가 -1 ~ 1 범위로 조정됨
        """
        # 신호들을 더하기
        mixed = np.sum(signals, axis=0)

        if normalize:
            # 오버플로우 방지
            max_val = np.max(np.abs(mixed))
            if max_val > 1.0:
                mixed = mixed / max_val

        return mixed.astype(np.float32)

    def add_silence(self, duration):
        """
        무음 신호 생성

        Args:
            duration: 지속 시간 (초)

        Returns:
            1D numpy 배열 (모두 0)
        """
        num_samples = int(self.sample_rate * duration)
        return np.zeros(num_samples, dtype=np.float32)

    def apply_envelope(self, waveform, envelope_points):
        """
        사용자 정의 앰벨로프 적용

        시간에 따라 신호의 크기를 변조합니다.

        Args:
            waveform: 1D numpy 배열
            envelope_points: [(시간, 진폭), ...] 리스트
                            시간은 0 ~ 1 사이의 상대값

        Returns:
            numpy 배열 (앰벨로프 적용됨)

        예제:
            # 천천히 커졌다가 빠르게 작아지는 신호
            envelope = [(0.0, 0.0), (0.7, 1.0), (1.0, 0.0)]
            signal = synth.apply_envelope(tone, envelope)
        """
        if not envelope_points:
            return waveform

        # 앰벨로프 곡선 생성
        times = np.array([p[0] for p in envelope_points])
        amplitudes = np.array([p[1] for p in envelope_points])

        # 신호의 길이에 맞는 시간 배열
        signal_times = np.linspace(0, 1, len(waveform))

        # 보간 (interpolation)
        envelope_curve = np.interp(signal_times, times, amplitudes)

        # 앰벨로프 적용
        return (waveform * envelope_curve).astype(np.float32)

    @staticmethod
    def note_to_frequency(note, octave=4):
        """
        음표 이름을 주파수로 변환

        A4 = 440 Hz 표준을 사용합니다.

        Args:
            note: 음표 ('C', 'D', 'E', 'F', 'G', 'A', 'B')
            octave: 옥타브 (1 ~ 8)

        Returns:
            float: 주파수 (Hz)

        예제:
            >>> AudioSynthesizer.note_to_frequency('A', 4)
            440.0
            >>> AudioSynthesizer.note_to_frequency('C', 5)
            523.25...
        """
        # 음표별 기본 주파수 (4옥타브)
        notes = {
            'C': 261.63,
            'D': 293.66,
            'E': 329.63,
            'F': 349.23,
            'G': 392.00,
            'A': 440.00,
            'B': 493.88,
        }

        base_freq = notes[note.upper()]

        # 옥타브 조정 (한 옥타브 = 2배 주파수)
        return base_freq * (2 ** (octave - 4))
