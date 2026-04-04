"""
5-5.py: Reachy Mini SDK와 연동
Week 05 - 섹션 6: Reachy Mini SDK와 연동

Reachy Mini의 오디오 기능을 SDK와 연동하여 로봇의 동작과 음성을 결합합니다.

필요 라이브러리:
    uv add SpeechRecognition pyttsx3
    
참고: Reachy Mini SDK가 설치되어 있어야 합니다.
"""

import speech_recognition as sr
import pyttsx3
from reachy_mini import ReachyMini


class ReachyVoiceControl:
    def __init__(self):
        # Reachy Mini 연결
        self.reachy = ReachyMini(localhost_only=True)
        self.reachy.enable_motors()
        
        # 음성 시스템 초기화
        self.recognizer = sr.Recognizer()
        self.tts = pyttsx3.init()
        
        # 명령어 등록
        self.commands = {
            '위': lambda: self.look_direction(0.5, 0, 0.5),
            '아래': lambda: self.look_direction(0.5, 0, 0.2),
            '왼쪽': lambda: self.look_direction(0.5, 0.3, 0.35),
            '오른쪽': lambda: self.look_direction(0.5, -0.3, 0.35),
            '앞': lambda: self.look_direction(0.5, 0, 0.35),
        }
    
    def speak(self, text):
        """음성 출력"""
        print(f"[리치]: {text}")
        self.tts.say(text)
        self.tts.runAndWait()
    
    def listen(self):
        """음성 입력"""
        with sr.Microphone() as source:
            print("명령을 기다리는 중...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=5)
                return self.recognizer.recognize_google(audio, language='ko-KR')
            except:
                return None
    
    def look_direction(self, x, y, z):
        """지정된 방향 바라보기"""
        self.reachy.look_at_world(x=x, y=y, z=z, duration=1.0)
    
    def run(self):
        """메인 루프"""
        self.speak("음성 제어 모드를 시작합니다.")
        
        while True:
            text = self.listen()
            if text is None:
                continue
            
            print(f"인식: {text}")
            
            if '종료' in text:
                self.speak("음성 제어를 종료합니다.")
                break
            
            # 방향 명령 처리
            for keyword, action in self.commands.items():
                if keyword in text:
                    self.speak(f"{keyword}을 바라봅니다.")
                    action()
                    break
            else:
                self.speak("알 수 없는 명령입니다.")


if __name__ == "__main__":
    print("=" * 50)
    print("Week 05 - 6절: Reachy Mini SDK와 연동")
    print("=" * 50)
    print("\n사용 가능한 명령어:")
    print("  - '위': 위를 바라보기")
    print("  - '아래': 아래를 바라보기")
    print("  - '왼쪽': 왼쪽을 바라보기")
    print("  - '오른쪽': 오른쪽을 바라보기")
    print("  - '앞': 앞을 바라보기")
    print("  - '종료': 음성 제어 종료")
    print()
    
    controller = ReachyVoiceControl()
    controller.run()
