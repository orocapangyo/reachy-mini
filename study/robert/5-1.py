"""
5-1.py: Text-to-Speech (TTS) 구현 예제
Week 05 - 섹션 3.3: Text-to-Speech (TTS) 구현

이 파일은 두 가지 TTS 방식을 보여줍니다:
1. pyttsx3 - 오프라인 TTS (인터넷 불필요)
2. gTTS - 온라인 TTS (한국어 지원 우수)

필요 라이브러리:
    uv add pyttsx3 gTTS playsound
또는:
    pip install pyttsx3 gTTS playsound
"""

import os


def demo_pyttsx3():
    """pyttsx3 사용 (오프라인 TTS) 예제"""
    print("=" * 50)
    print("pyttsx3 오프라인 TTS 예제")
    print("=" * 50)
    
    import pyttsx3
    
    # TTS 엔진 초기화
    engine = pyttsx3.init()
    
    # 음성 속성 설정
    engine.setProperty('rate', 150)    # 말하기 속도 (기본값: 200)
    engine.setProperty('volume', 0.9)  # 볼륨 (0.0 ~ 1.0)
    
    # 사용 가능한 음성 목록 확인
    voices = engine.getProperty('voices')
    for idx, voice in enumerate(voices):
        print(f"{idx}: {voice.name} - {voice.languages}")
    
    # 한국어 음성이 있으면 선택 (시스템에 따라 다름)
    # engine.setProperty('voice', voices[1].id)
    
    # 텍스트를 음성으로 변환하여 재생
    text = "안녕하세요, 저는 리치 미니입니다."
    print(f"\n말하는 중: {text}")
    engine.say(text)
    engine.runAndWait()
    
    print("TTS 재생이 완료되었습니다.\n")


def demo_gtts():
    """gTTS 사용 (온라인 TTS - 한국어 지원) 예제"""
    print("=" * 50)
    print("gTTS 온라인 TTS 예제 (한국어 지원)")
    print("=" * 50)
    
    from gtts import gTTS
    
    # 한국어 텍스트
    text = "안녕하세요, 저는 리치 미니입니다. 만나서 반갑습니다."
    
    # gTTS로 음성 생성 (한국어)
    tts = gTTS(text=text, lang='ko', slow=False)
    
    # MP3 파일로 저장
    output_file = "greeting.mp3"
    tts.save(output_file)
    print(f"음성 파일이 '{output_file}'에 저장되었습니다.")
    
    # 파일 재생 (시스템에 따라 다른 방법 사용)
    # Windows
    os.system(f"start {output_file}")
    # macOS: os.system(f"afplay {output_file}")
    # Linux: os.system(f"mpg123 {output_file}")
    
    print("gTTS 재생이 완료되었습니다.\n")


def main():
    """메인 함수 - 두 가지 TTS 방식 데모 실행"""
    print("\n" + "=" * 50)
    print("Week 05 - 3.3절: Text-to-Speech (TTS) 구현 예제")
    print("=" * 50 + "\n")
    
    while True:
        print("실행할 예제를 선택하세요:")
        print("1. pyttsx3 (오프라인 TTS)")
        print("2. gTTS (온라인 TTS - 한국어 지원)")
        print("3. 두 가지 모두 실행")
        print("0. 종료")
        
        choice = input("\n선택 (0-3): ").strip()
        
        if choice == '1':
            demo_pyttsx3()
        elif choice == '2':
            demo_gtts()
        elif choice == '3':
            demo_pyttsx3()
            demo_gtts()
        elif choice == '0':
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 선택입니다. 다시 선택해 주세요.\n")


if __name__ == "__main__":
    main()
