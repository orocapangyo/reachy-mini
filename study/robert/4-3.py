"""
화살표 키로 Reachy Mini 머리를 제어하는 예제

조작법:
  ↑ (위): Z 위치 증가 (머리 위로)
  ↓ (아래): Z 위치 감소 (머리 아래로)
  ← (왼쪽): Y 위치 감소 (왼쪽 바라보기)
  → (오른쪽): Y 위치 증가 (오른쪽 바라보기)
  Q: 종료
"""

import msvcrt
from reachy_mini import ReachyMini

# 초기 위치 설정
x = 0.5  # 전방 거리 (고정)
y = 0.0  # 좌우 위치
z = 0.4  # 높이

# 이동 단위
step = 0.05

print("화살표 키로 Reachy Mini 머리를 제어합니다.")
print("↑/↓: 위/아래, ←/→: 왼쪽/오른쪽, Q: 종료")
print(f"초기 위치: x={x}, y={y}, z={z}")

with ReachyMini(media_backend="no_media") as reachy:
    # 초기 위치로 이동
    reachy.look_at_world(x=x, y=y, z=z, duration=1.0)
    
    try:
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                
                # 화살표 키는 2바이트: 첫 번째가 0xe0 또는 0x00
                if key == b'\xe0' or key == b'\x00':
                    arrow = msvcrt.getch()
                    
                    if arrow == b'H':  # 위 화살표
                        z += step
                        print(f"↑ 위로: z={z:.2f}")
                    elif arrow == b'P':  # 아래 화살표
                        z -= step
                        print(f"↓ 아래로: z={z:.2f}")
                    elif arrow == b'K':  # 왼쪽 화살표
                        y -= step
                        print(f"← 왼쪽: y={y:.2f}")
                    elif arrow == b'M':  # 오른쪽 화살표
                        y += step
                        print(f"→ 오른쪽: y={y:.2f}")
                    
                    # 범위 제한
                    y = max(-0.5, min(0.5, y))
                    z = max(0.1, min(0.8, z))
                    
                    # 머리 이동
                    reachy.look_at_world(x=x, y=y, z=z, duration=0.3)
                
                elif key.lower() == b'q':
                    print("종료합니다.")
                    break
                    
    except KeyboardInterrupt:
        print("\n종료합니다.")
    finally:
        print("화살표 키 제어 예제를 종료합니다.")
