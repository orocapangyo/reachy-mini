"""
5-4.py: 통합 예제 - 음성 대화 시스템
Week 05 - 섹션 5: 통합 예제: 음성 대화 시스템

마이크 입력, 음성 인식, TTS를 통합한 간단한 음성 대화 시스템입니다.

필요 라이브러리:
    uv add SpeechRecognition pyttsx3
"""

import speech_recognition as sr
import pyttsx3
import time


class VoiceAssistant:
    def __init__(self):
        # 음성 인식기 초기화
        self.recognizer = sr.Recognizer()
        
        # TTS 엔진 초기화
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        
        # 명령어 매핑
        self.commands = {
            '안녕': self.greet,
            '시간': self.tell_time,
            '종료': self.shutdown,
        }
        
        self.running = True
    
    def speak(self, text):
        """텍스트를 음성으로 출력"""
        print(f"[리치 미니]: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen(self):
        """마이크에서 음성 입력을 받아 텍스트로 변환"""
        with sr.Microphone() as source:
            print("\n듣고 있습니다...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio, language='ko-KR')
                print(f"[사용자]: {text}")
                return text
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                return None
            except sr.RequestError:
                self.speak("음성 인식 서비스에 연결할 수 없습니다.")
                return None
    
    def greet(self):
        """인사 응답"""
        self.speak("안녕하세요! 저는 리치 미니입니다. 무엇을 도와드릴까요?")
    
    def tell_time(self):
        """현재 시간 알려주기"""
        current_time = time.strftime("%H시 %M분")
        self.speak(f"현재 시간은 {current_time}입니다.")
    
    def shutdown(self):
        """시스템 종료"""
        self.speak("안녕히 가세요!")
        self.running = False
    
    def process_command(self, text):
        """명령어 처리"""
        if text is None:
            return
        
        # 등록된 명령어 확인
        for keyword, action in self.commands.items():
            if keyword in text:
                action()
                return
        
        # 알 수 없는 명령어
        self.speak(f"'{text}'를 이해하지 못했습니다. 다시 말씀해 주세요.")
    
    def run(self):
        """메인 루프 실행"""
        self.speak("음성 대화 시스템을 시작합니다.")
        
        while self.running:
            text = self.listen()
            self.process_command(text)
        
        print("음성 대화 시스템을 종료합니다.")


if __name__ == "__main__":
    print("=" * 50)
    print("Week 05 - 5절: 통합 예제 - 음성 대화 시스템")
    print("=" * 50)
    print("\n사용 가능한 명령어:")
    print("  - '안녕': 인사")
    print("  - '시간': 현재 시간")
    print("  - '종료': 시스템 종료")
    print()
    
    assistant = VoiceAssistant()
    assistant.run()
