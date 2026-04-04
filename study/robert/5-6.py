"""
5-6.py: Reachy Mini 음성 제어 (일반 노트북 마이크 사용) - 개선 버전
Week 05 - 섹션 6 변형: 노트북 마이크를 사용한 Reachy Mini 제어

개선 사항:
- 주변 소음 적응 시간 증가
- 음성 인식 감도 조정
- 더 긴 대기 시간
- Whisper 옵션 추가 (오프라인, 더 높은 정확도)

필요 라이브러리:
    uv add SpeechRecognition pyttsx3
    
Whisper 사용 시:
    uv add openai-whisper sounddevice numpy
"""

import speech_recognition as sr
import pyttsx3
import sys

# Whisper 사용 여부 (True로 변경하면 Whisper 사용)
USE_WHISPER = False

if USE_WHISPER:
    import whisper
    import sounddevice as sd
    import numpy as np


class ReachyVoiceControl:
    """노트북 마이크를 사용한 Reachy Mini 음성 제어 클래스"""
    
    def __init__(self, use_reachy=True):
        """음성 제어 시스템 초기화"""
        self.use_reachy = use_reachy
        
        if use_reachy:
            print("Reachy Mini에 연결 중...")
            from reachy_mini import ReachyMini
            self.reachy = ReachyMini(
                localhost_only=True,
                media_backend='no_media'
            )
            self.reachy.enable_motors()
            print("Reachy Mini 연결 완료!")
        else:
            print("⚠️  Reachy Mini 없이 음성 인식만 테스트합니다.")
            self.reachy = None
        
        # 음성 인식기 초기화
        self.recognizer = sr.Recognizer()
        
        # 음성 인식 감도 설정 (값이 낮을수록 더 민감)
        self.recognizer.energy_threshold = 300  # 기본값은 300
        self.recognizer.dynamic_energy_threshold = True  # 동적 조절 활성화
        self.recognizer.pause_threshold = 0.8  # 말 끝났다고 판단하는 시간 (초)
        
        # TTS 엔진 초기화
        self.tts = pyttsx3.init()
        self.tts.setProperty('rate', 150)
        
        # Whisper 모델 로드 (USE_WHISPER가 True인 경우)
        if USE_WHISPER:
            print("Whisper 모델 로드 중...")
            self.whisper_model = whisper.load_model("base")
            print("Whisper 모델 로드 완료!")
        
        # 명령어 등록
        self.commands = {
            '위': lambda: self.look_direction(0.5, 0, 0.5),
            '아래': lambda: self.look_direction(0.5, 0, 0.2),
            '왼쪽': lambda: self.look_direction(0.5, 0.3, 0.35),
            '오른쪽': lambda: self.look_direction(0.5, -0.3, 0.35),
            '앞': lambda: self.look_direction(0.5, 0, 0.35),
            '일어나': lambda: self.wake_up(),
            '자': lambda: self.go_sleep(),
        }
        
        self.running = True
    
    def speak(self, text):
        """텍스트를 음성으로 출력"""
        print(f"🔊 [리치]: {text}")
        self.tts.say(text)
        self.tts.runAndWait()
    
    def listen_google(self):
        """Google Speech Recognition으로 음성 인식 (온라인)"""
        with sr.Microphone() as source:
            print("\n" + "=" * 40)
            print("🎤 주변 소음 분석 중... (2초)")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print(f"   에너지 임계값: {self.recognizer.energy_threshold:.0f}")
            print("=" * 40)
            print("📢 지금 말씀하세요!")
            print("   (5초 안에 말을 시작하세요)")
            print("=" * 40)
            
            try:
                audio = self.recognizer.listen(
                    source, 
                    timeout=5,  # 말 시작까지 대기 시간
                    phrase_time_limit=10  # 최대 말하기 시간
                )
                print("🔄 인식 중...")
                
                text = self.recognizer.recognize_google(audio, language='ko-KR')
                print(f"✅ [인식 결과]: {text}")
                return text
                
            except sr.WaitTimeoutError:
                print("⏰ 시간 초과: 말씀이 없었습니다.")
                return None
            except sr.UnknownValueError:
                print("❓ 음성을 인식할 수 없습니다. 더 크게 말씀해 주세요.")
                return None
            except sr.RequestError as e:
                print(f"❌ Google 음성 인식 서비스 오류: {e}")
                return None
    
    def listen_whisper(self):
        """Whisper로 음성 인식 (오프라인, 더 정확함)"""
        SAMPLE_RATE = 16000
        DURATION = 5
        
        print("\n" + "=" * 40)
        print(f"🎤 {DURATION}초 동안 녹음합니다...")
        print("📢 지금 말씀하세요!")
        print("=" * 40)
        
        try:
            audio = sd.rec(
                int(DURATION * SAMPLE_RATE),
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype='float32'
            )
            sd.wait()
            print("🔄 Whisper로 인식 중... (잠시 기다려 주세요)")
            
            audio_data = audio.flatten().astype(np.float32)
            result = self.whisper_model.transcribe(audio_data, language='ko', fp16=False)
            text = result['text'].strip()
            
            if text:
                print(f"✅ [인식 결과]: {text}")
                return text
            else:
                print("❓ 음성을 인식할 수 없습니다.")
                return None
                
        except Exception as e:
            print(f"❌ Whisper 오류: {e}")
            return None
    
    def listen(self):
        """음성 인식 (설정에 따라 Google 또는 Whisper 사용)"""
        if USE_WHISPER:
            return self.listen_whisper()
        else:
            return self.listen_google()
    
    def look_direction(self, x, y, z):
        """지정된 방향 바라보기"""
        if self.reachy:
            try:
                self.reachy.look_at_world(x=x, y=y, z=z, duration=1.0)
                print(f"   👀 바라보는 방향: ({x}, {y}, {z})")
            except Exception as e:
                print(f"   ❌ 동작 오류: {e}")
        else:
            print(f"   [시뮬레이션] 바라보는 방향: ({x}, {y}, {z})")
    
    def wake_up(self):
        """로봇 깨우기"""
        if self.reachy:
            try:
                self.reachy.wake_up()
            except Exception as e:
                print(f"   ❌ 동작 오류: {e}")
        else:
            print("   [시뮬레이션] 로봇이 일어납니다.")
    
    def go_sleep(self):
        """로봇 재우기"""
        if self.reachy:
            try:
                self.reachy.goto_sleep()
            except Exception as e:
                print(f"   ❌ 동작 오류: {e}")
        else:
            print("   [시뮬레이션] 로봇이 잠듭니다.")
    
    def process_command(self, text):
        """명령어 처리"""
        if text is None:
            return
        
        # 종료 명령 확인
        if '종료' in text or '끝' in text:
            self.speak("음성 제어를 종료합니다.")
            self.running = False
            return
        
        # 등록된 명령어 확인
        for keyword, action in self.commands.items():
            if keyword in text:
                self.speak(f"{keyword} 명령을 수행합니다.")
                action()
                return
        
        # 알 수 없는 명령어
        print(f"   ℹ️  '{text}'는 등록된 명령어가 아닙니다.")
    
    def run(self):
        """메인 루프"""
        self.speak("음성 제어를 시작합니다.")
        
        while self.running:
            text = self.listen()
            self.process_command(text)
        
        print("\n👋 음성 제어를 종료합니다.")
        if self.reachy:
            self.reachy.disable_motors()


def main():
    """메인 함수"""
    print("=" * 60)
    print("🤖 Reachy Mini 음성 제어 (노트북 마이크 사용)")
    print("=" * 60)
    
    # 모드 선택
    print("\n실행 모드를 선택하세요:")
    print("  1. Reachy Mini 연결 (데몬 필요)")
    print("  2. 음성 인식만 테스트 (데몬 불필요)")
    
    choice = input("\n선택 (1 또는 2): ").strip()
    use_reachy = choice != '2'
    
    print("\n" + "-" * 60)
    print("📋 사용 가능한 명령어:")
    print("   '위', '아래', '왼쪽', '오른쪽', '앞'  : 방향 바라보기")
    print("   '일어나', '자'                        : 로봇 상태 변경")
    print("   '종료' 또는 '끝'                      : 프로그램 종료")
    print("-" * 60)
    
    if USE_WHISPER:
        print("\n🧠 음성 인식: Whisper (오프라인, 높은 정확도)")
    else:
        print("\n🌐 음성 인식: Google Speech Recognition (온라인)")
    
    print("\n💡 팁: 조용한 환경에서 또렷하게 말씀해 주세요.")
    print()
    
    try:
        controller = ReachyVoiceControl(use_reachy=use_reachy)
        controller.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자가 중단했습니다. (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        if "Connection" in str(e) or "timeout" in str(e):
            print("\n💡 Reachy Mini 데몬이 실행 중인지 확인하세요:")
            print("   uv run reachy-mini-daemon --sim")


if __name__ == "__main__":
    main()
