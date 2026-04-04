"""
Week 07 종합 테스트: 비전-동작 통합 시스템 (시뮬레이션)

노트북 카메라로 얼굴을 검출하고 MuJoCo 시뮬레이션의 Reachy Mini가 반응하는 시스템

실행 전 준비사항:
1. 터미널 1에서 시뮬레이션 실행: reachy-mini-daemon --sim
2. 터미널 2에서 이 스크립트 실행: python 7-1.py

종료: 'q' 키 입력
"""

import cv2
import time
import numpy as np
from enum import Enum
from reachy_mini import ReachyMini

# 감정 인식 라이브러리 (선택적)
try:
    from fer import FER
    HAS_FER = True
except ImportError:
    HAS_FER = False
    print("⚠️  FER 라이브러리가 설치되지 않았습니다. 감정 인식 기능이 비활성화됩니다.")
    print("   설치: uv pip install fer")


class RobotState(Enum):
    """로봇 상태"""
    IDLE = "idle"
    DETECTING_FACE = "detecting_face"
    TRACKING_FACE = "tracking_face"
    REACTING_EMOTION = "reacting_emotion"


class VisionMotionIntegration:
    """비전-동작 통합 시스템"""
    
    def __init__(self, use_emotion=False):
        """
        초기화
        
        Args:
            use_emotion: 감정 인식 사용 여부
        """
        print("\n" + "="*60)
        print("Week 07: 비전-동작 통합 시스템 초기화 중...")
        print("="*60)
        
        # MuJoCo 시뮬레이션 연결
        print("\n[1/4] MuJoCo 시뮬레이션 연결 중...")
        try:
            self.reachy = ReachyMini()
            print("✅ 시뮬레이션 연결 성공")
        except Exception as e:
            print(f"❌ 시뮬레이션 연결 실패: {e}")
            print("\n💡 해결방법:")
            print("   터미널 1에서 실행: reachy-mini-daemon --sim")
            raise
        
        # 노트북 카메라 연결
        print("\n[2/4] 노트북 카메라 연결 중...")
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            # 다른 인덱스 시도
            print("   카메라 인덱스 0 실패, 인덱스 1 시도 중...")
            self.cap = cv2.VideoCapture(1)
            
        if not self.cap.isOpened():
            print("❌ 카메라를 열 수 없습니다!")
            raise RuntimeError("카메라 연결 실패")
        
        # 카메라 설정
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        print(f"✅ 카메라 연결 성공: {width}x{height} @ {fps}fps")
        
        # 얼굴 검출기 로드
        print("\n[3/4] 얼굴 검출기 로드 중...")
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        print("✅ Haar Cascade 얼굴 검출기 로드 완료")
        
        # 감정 인식기 (선택적)
        print("\n[4/4] 감정 인식기 초기화 중...")
        self.use_emotion = use_emotion and HAS_FER
        if self.use_emotion:
            self.emotion_detector = FER(mtcnn=False)  # 빠른 처리를 위해 MTCNN 비활성화
            print("✅ FER 감정 인식기 초기화 완료")
        else:
            self.emotion_detector = None
            if use_emotion and not HAS_FER:
                print("⚠️  FER 미설치로 감정 인식 비활성화")
            else:
                print("ℹ️  감정 인식 기능 비활성화 (use_emotion=False)")
        
        # 상태 변수
        self.state = RobotState.IDLE
        self.last_face_time = 0
        self.last_emotion_time = 0
        self.current_emotion = "unknown"
        
        # 설정값
        self.emotion_cooldown = 3.0  # 감정 분석 간격 (초)
        self.idle_timeout = 5.0  # IDLE로 전환 시간 (초)
        
        # 통계
        self.frame_count = 0
        self.face_detect_count = 0
        self.start_time = time.time()
        
        print("\n" + "="*60)
        print("✅ 초기화 완료!")
        print("="*60 + "\n")
    
    def process_frame(self):
        """
        프레임 처리 (얼굴 검출 + 감정 인식 + 로봇 제어)
        
        Returns:
            처리된 프레임 (numpy array) 또는 None
        """
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        self.frame_count += 1
        current_time = time.time()
        
        # 그레이스케일 변환 (얼굴 검출용)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 얼굴 검출
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5,
            minSize=(60, 60)
        )
        
        if len(faces) > 0:
            self.face_detect_count += 1
            self.last_face_time = current_time
            self.state = RobotState.TRACKING_FACE
            
            # 가장 큰 얼굴 선택 (가장 가까운 사람)
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = largest_face
            
            # 얼굴 사각형 그리기
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # 얼굴 중심 좌표
            center_x = x + w // 2
            center_y = y + h // 2
            cv2.circle(frame, (center_x, center_y), 5, (255, 0, 0), -1)
            
            # 이미지 중심을 기준으로 상대 위치 계산
            img_h, img_w = frame.shape[:2]
            offset_x = (center_x - img_w / 2) / img_w
            offset_y = (center_y - img_h / 2) / img_h
            
            # MuJoCo 시뮬레이션 좌표 계산
            # X: 로봇 전방 거리 (0.5m 고정)
            # Y: 좌우 (-0.3 ~ +0.3m)
            # Z: 상하 (0.1 ~ 0.5m, 기본 0.3m)
            target_x = 0.5
            target_y = -offset_x * 0.3  # 화면 왼쪽(-) → 로봇 오른쪽(+)
            target_z = -offset_y * 0.3 + 0.3  # 화면 위(-) → 로봇 위(+)
            
            # 로봇 시선 제어
            try:
                self.reachy.head.look_at(
                    x=target_x, 
                    y=target_y, 
                    z=target_z, 
                    duration=0.2
                )
            except Exception as e:
                print(f"⚠️  look_at 오류: {e}")
            
            # 좌표 정보 표시
            coord_text = f"Target: ({target_x:.2f}, {target_y:.2f}, {target_z:.2f})"
            cv2.putText(frame, coord_text, (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            # 감정 인식 (일정 간격마다)
            if self.use_emotion and (current_time - self.last_emotion_time > self.emotion_cooldown):
                self.analyze_emotion(frame)
                self.last_emotion_time = current_time
            
            # 감정 정보 표시
            if self.current_emotion != "unknown":
                emotion_text = f"Emotion: {self.current_emotion}"
                cv2.putText(frame, emotion_text, (10, 90), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        else:
            # 얼굴이 보이지 않음
            if current_time - self.last_face_time > self.idle_timeout:
                self.state = RobotState.IDLE
                self.current_emotion = "unknown"
        
        # 상태 정보 표시
        state_color = {
            RobotState.IDLE: (128, 128, 128),
            RobotState.TRACKING_FACE: (0, 255, 0),
            RobotState.REACTING_EMOTION: (0, 255, 255)
        }
        
        state_text = f"State: {self.state.value.upper()}"
        cv2.putText(frame, state_text, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                    state_color.get(self.state, (255, 255, 255)), 2)
        
        # FPS 표시
        elapsed = current_time - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        fps_text = f"FPS: {fps:.1f}"
        cv2.putText(frame, fps_text, (img_w - 120, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # 얼굴 검출 횟수
        face_text = f"Faces: {self.face_detect_count}"
        cv2.putText(frame, face_text, (img_w - 120, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def analyze_emotion(self, frame):
        """
        감정 분석
        
        Args:
            frame: 입력 프레임
        """
        if not self.use_emotion:
            return
        
        try:
            emotions = self.emotion_detector.detect_emotions(frame)
            
            if emotions and len(emotions) > 0:
                # 가장 큰 얼굴의 감정
                top_emotion_dict = emotions[0]['emotions']
                dominant = max(top_emotion_dict, key=top_emotion_dict.get)
                confidence = top_emotion_dict[dominant]
                
                # 신뢰도가 일정 수준 이상일 때만 업데이트
                if confidence > 0.3:
                    self.current_emotion = f"{dominant} ({confidence:.0%})"
                    print(f"🎭 감정: {self.current_emotion}")
                    
                    # 감정에 따른 동작 (로그만 출력)
                    if dominant == 'happy' and confidence > 0.5:
                        print("   → 기쁜 반응! (여기서 동작 재생 가능)")
                    elif dominant == 'sad' and confidence > 0.5:
                        print("   → 위로 반응! (여기서 동작 재생 가능)")
                    elif dominant == 'surprise' and confidence > 0.5:
                        print("   → 놀란 반응! (여기서 동작 재생 가능)")
                
        except Exception as e:
            print(f"⚠️  감정 분석 오류: {e}")
    
    def run(self):
        """메인 루프 실행"""
        print("\n" + "="*60)
        print("시스템 실행 중...")
        print("="*60)
        print("📹 노트북 카메라: 얼굴 및 감정 인식")
        print("🤖 MuJoCo 시뮬레이션: Reachy Mini 동작 제어")
        if self.use_emotion:
            print("🎭 감정 인식: 활성화")
        else:
            print("🎭 감정 인식: 비활성화")
        print("\n종료: 'q' 키 입력")
        print("="*60 + "\n")
        
        try:
            while True:
                frame = self.process_frame()
                
                if frame is not None:
                    # 화면 표시
                    cv2.imshow('Week 07: Vision-Motion Integration (Simulation)', frame)
                
                # 키 입력 확인
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n👋 종료 요청을 받았습니다.")
                    break
                elif key == ord('e'):
                    # 감정 인식 토글
                    if HAS_FER:
                        self.use_emotion = not self.use_emotion
                        status = "활성화" if self.use_emotion else "비활성화"
                        print(f"\n🎭 감정 인식: {status}")
                    else:
                        print("\n⚠️  FER 라이브러리가 설치되지 않았습니다.")
                elif key == ord('s'):
                    # 통계 출력
                    self.print_statistics()
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Ctrl+C로 종료됨")
        
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.cleanup()
    
    def print_statistics(self):
        """통계 정보 출력"""
        elapsed = time.time() - self.start_time
        print("\n" + "="*60)
        print("📊 통계 정보")
        print("="*60)
        print(f"실행 시간: {elapsed:.1f}초")
        print(f"처리 프레임: {self.frame_count}개")
        print(f"평균 FPS: {self.frame_count / elapsed:.1f}")
        print(f"얼굴 검출: {self.face_detect_count}회")
        print(f"현재 상태: {self.state.value}")
        print(f"현재 감정: {self.current_emotion}")
        print("="*60 + "\n")
    
    def cleanup(self):
        """리소스 정리"""
        print("\n리소스 정리 중...")
        
        # 통계 출력
        self.print_statistics()
        
        # 카메라 해제
        if self.cap is not None:
            self.cap.release()
            print("✅ 카메라 해제 완료")
        
        # 창 닫기
        cv2.destroyAllWindows()
        print("✅ 창 닫기 완료")
        
        print("\n" + "="*60)
        print("프로그램 종료")
        print("="*60)


def main():
    """메인 함수"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║  Week 07: 비전-동작 통합 시스템 (시뮬레이션)                 ║
    ║                                                              ║
    ║  노트북 카메라 + MuJoCo 시뮬레이션 통합 테스트               ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # 사용자 선택
    print("\n감정 인식 기능을 사용하시겠습니까?")
    print("  y: 사용 (FER 라이브러리 필요)")
    print("  n: 사용 안 함 (얼굴 추적만)")
    
    choice = input("\n선택 (y/n, 기본값: n): ").strip().lower()
    use_emotion = (choice == 'y')
    
    # 시스템 초기화 및 실행
    try:
        system = VisionMotionIntegration(use_emotion=use_emotion)
        system.run()
    except Exception as e:
        print(f"\n❌ 시스템 시작 실패: {e}")
        print("\n💡 문제 해결:")
        print("   1. MuJoCo 시뮬레이션 실행 확인: reachy-mini-daemon --sim")
        print("   2. 카메라가 다른 프로그램에서 사용 중인지 확인")
        print("   3. 필요한 패키지 설치:")
        print("      uv pip install opencv-python")
        print("      uv pip install fer  (감정 인식용)")


if __name__ == "__main__":
    main()
