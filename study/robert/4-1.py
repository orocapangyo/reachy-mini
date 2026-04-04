import cv2
import time
from reachy_mini.media.media_manager import MediaManager, MediaBackend

def main():
    print("Reachy Mini Mujoco 시뮬레이션 카메라 영상 취득 시작...")
    
    # MediaManager 초기화 (Mujoco 시뮬레이션용)
    # use_sim=True 설정으로 UDP 카메라 스트림을 사용하도록 합니다.
    # 이 때, Mujoco 시뮬레이션 환경이 'udp://@127.0.0.1:5005'로 카메라 스트림을 송출하고 있어야 합니다.
    media_manager = MediaManager(backend=MediaBackend.DEFAULT, use_sim=True)

    try:
        # 카메라 영상 취득 및 표시
        while True:
            frame = media_manager.get_frame()
            if frame is not None:
                cv2.imshow("Reachy Mini Camera Feed (Mujoco Simulation)", frame)
            
            # 'q' 키를 누르면 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            time.sleep(0.01) # 짧은 대기 시간

    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        # 리소스 해제
        media_manager.close()
        cv2.destroyAllWindows()
        print("Reachy Mini Mujoco 시뮬레이션 카메라 영상 취득 종료.")

if __name__ == "__main__":
    main()
