"""
5-2.py: 음성 인식 기본 예제
Week 05 - 섹션 4.2: 음성 인식 기본 예제

마이크에서 음성을 인식하여 텍스트로 변환하는 예제입니다.

필요 라이브러리:
    uv add SpeechRecognition
또는:
    pip install SpeechRecognition
"""

import speech_recognition as sr


def main():
    """음성 인식 기본 예제"""
    print("=" * 50)
    print("Week 05 - 4.2절: 음성 인식 기본 예제")
    print("=" * 50)
    
    # 음성 인식기 초기화
    recognizer = sr.Recognizer()
    
    # 마이크에서 음성 입력 받기
    with sr.Microphone() as source:
        print("주변 소음을 분석 중...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("말씀하세요...")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        
    print("인식 중...")
    
    try:
        # Google Speech Recognition API 사용 (무료, 인터넷 필요)
        text = recognizer.recognize_google(audio, language='ko-KR')
        print(f"인식 결과: {text}")
    except sr.UnknownValueError:
        print("음성을 인식할 수 없습니다.")
    except sr.RequestError as e:
        print(f"Google Speech Recognition 서비스 오류: {e}")


if __name__ == "__main__":
    main()
