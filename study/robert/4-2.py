import time
from reachy_mini import ReachyMini

# Reachy Mini 인스턴스 생성
# media_backend="no_media"로 카메라 없이 연결합니다.
print("Reachy Mini가 여러 지점을 바라봅니다.")

with ReachyMini(media_backend="no_media") as reachy:
    try:
        # 1. (0.5, 0, 0.3) 지점 (로봇 전방 50cm, 높이 30cm) 바라보기
        print("Point 1: (0.5, 0, 0.3)")
        reachy.look_at_world(x=0.5, y=0, z=0.3, duration=2.0)
        time.sleep(2)

        # 2. (0.3, 0.2, 0.5) 지점 (로봇 전방 30cm, 오른쪽 20cm, 높이 50cm) 바라보기
        print("Point 2: (0.3, 0.2, 0.5)")
        reachy.look_at_world(x=0.3, y=0.2, z=0.5, duration=2.0)
        time.sleep(2)

        # 3. (0.3, -0.2, 0.5) 지점 (로봇 전방 30cm, 왼쪽 20cm, 높이 50cm) 바라보기
        print("Point 3: (0.3, -0.2, 0.5)")
        reachy.look_at_world(x=0.3, y=-0.2, z=0.5, duration=2.0)
        time.sleep(2)

    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        print("look_at 기능 예제를 종료합니다.")
