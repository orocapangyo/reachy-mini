## 4주차: 센서 활용 - 카메라
- reachy-mini-daemon --sim --scene minimal
  테이블 있는 가상화면 환경 설정

### 1. Reachy Mini의 카메라 시스템 이해
Reachy Mini는 두 개의 카메라(왼쪽 눈, 오른쪽 눈)를 통해 주변 환경을 인식할 수 있습니다. 이 카메라는 로봇이 물체를 추적하거나 환경과 상호작용하는 데 필수적인 시각 정보를 제공합니다.

#### 1.2 Python SDK를 이용한 카메라 영상 취득
<img width="800" height="500" alt="4-1" src="https://github.com/user-attachments/assets/6bbe9415-b040-4abe-aa9f-c833307bb9fd" />

### 2. OpenCV를 활용한 영상 처리
#### 2.1 OpenCV 설치

Python 환경에서 OpenCV를 설치하는 가장 쉬운 방법은 `pip`를 사용하는 것입니다.

```bash
pip install opencv-python numpy
```
#### 2.2 기본적인 영상 처리 기술

**2.2.1 그레이스케일 변환**
컬러 이미지를 흑백 이미지로 변환하여 처리 속도를 높이거나 특정 알고리즘에 적합한 형태로 만듭니다.

<img width="800" height="500" alt="4-2" src="https://github.com/user-attachments/assets/b5f1720b-05bb-4a38-8425-c5fdbe8af957" />

**2.2.2 블러링 (Blurring)**
이미지의 노이즈를 제거하거나 세부 정보를 부드럽게 만들어 특징 추출에 용이하게 합니다. 가우시안 블러가 일반적으로 사용됩니다.

<img width="800" height="500" alt="4-3" src="https://github.com/user-attachments/assets/83f2890b-890c-4e80-a6ac-ff083b510ada" />

**2.2.3 엣지 검출 (Edge Detection)**
이미지의 경계를 찾아 객체의 윤곽을 식별하는 데 사용됩니다. Canny 엣지 검출이 대표적입니다.

<img width="800" height="500" alt="4-4" src="https://github.com/user-attachments/assets/e0d9dc4e-26ae-474f-a1d4-6efe0ac3997e" />

**2.2.4 색상 기반 객체 검출 (HSV 마스크)**
특정 색상을 가진 객체를 이미지에서 분리하는 데 유용합니다. RGB 대신 HSV(Hue, Saturation, Value) 색상 공간을 사용하면 색상 변화에 더 강인하게 반응합니다.

<img width="1481" height="865" alt="4-5" src="https://github.com/user-attachments/assets/a4b5f621-bccc-4d2e-b323-009026013a32" />

```python

import cv2
import time
from reachy_mini import ReachyMini

# Reachy Mini 연결
with ReachyMini() as mini:
    print("카메라 스트림을 시작합니다. 'q' 키를 눌러 종료하세요.")
    
    while True:
        frame = mini.media.get_frame()

        if frame is not None:
            
            # OpenCV를 사용하여 창에 이미지 표시
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            #빨간색 객체를 검출하기 위한 HSV 범위(예시)
            lower_red = (0,120,70)
            upper_red = (10,255,255)

            # HSV 이미지에서 지정된 범위의 색상만 추출하여 마스크 생성
            mask = cv2.inRange(hsv_frame, lower_red, upper_red)

            # 원본 이미지와 마스크를 AND 연산하여 빨간색 객체만 표시
            res = cv2.bitwise_and(frame, frame, mask=mask)

            cv2.imshow('red Object Mask', mask)
            cv2.imshow('red Object Detected', res)
            cv2.imshow('Reachy Mini Camera Feed(Left)', frame)
            

            
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray_frame, 100, 200)
            cv2.imshow('Edges', edges)
            cv2.imshow('Reachy Mini Camera Feed(Left)', frame)
            

            #blurred_frame = cv2.GaussianBlur(frame, (5, 5), 0)
            #cv2.imshow('Blurred Feed', blurred_frame)
           #cv2.imshow('Reachy Mini Camera Feed(Left)', frame)
        else:
            # 프레임이 아직 준비되지 않았을 때
            print("프레임을 불러오는 중...")
            time.sleep(0.1)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
```

### 3. Reachy Mini `look_at` 기능 구현
`look_at` 기능은 Reachy Mini가 특정 3D 공간 좌표를 바라보도록 헤드를 움직이는 강력한 기능입니다. 이는 로봇이 특정 사람이나 물체에 시선을 고정하게 하여 자연스러운 상호작용을 가능하게 합니다.

#### 3.3 예제: 특정 3D 공간 좌표 바라보기
<img width="800" height="500" alt="4-6" src="https://github.com/user-attachments/assets/a3e0dd5a-f239-4834-851d-1713400ada20" />

```python

import time
import cv2
import threading

from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose


reachy = ReachyMini(host ='localhost')


reachy.enable_motors()
pose = create_head_pose(pitch=20, yaw=15, degrees=True)
pose1 = create_head_pose(x=0.3, y=0.2, z=0.5)
pose2 = create_head_pose(x=0.3, y=-0.2, z=0.5)

with ReachyMini() as mini:
    print("카메라 스트림을 시작합니다. 'q' 키를 눌러 종료하세요.")
    print("Reachy Mini가 여러 지점을 바라봅니다.")

def move_head():
    try:
        
            # 전방 50cm, 높이 30cm
            print("point 1: (0.5, 0, 0.3)")
            reachy.goto_target(head=pose, duration=2.0)
            time.sleep(2)

            # 전방 30cm, 오른쪽 20cm, 높이 50cm
            print("point 2: (0.3, 0.5, 0.5)")
            reachy.goto_target(head=pose1, duration=2.0)
            time.sleep(2)

            # 전방 30cm, 왼쪽 20cm, 높이 50cm
            print("point 3: (0.1, -0.5, 0.2)")
            reachy.goto_target(head=pose2, duration=2.0)
            time.sleep(2)

    except KeyboardInterrupt:
        print(f"오류 발생:{e}")


try:
    movement_thread = threading.Thread(target=move_head)
    movement_thread.start()
    print("카메라 스트림을 시작합니다.")
    print("'q'키를 누르면 종료합니다.")

    while True:

         frame = reachy.media.get_frame()

         if frame is not None:

              cv2.imshow("Reachy Mini Camera", frame)

         if cv2.waitKey(1) & 0xFF == ord('q'):
            break
         
except Exception as e:

    print(f"오류 발생: {e}")


finally:
    #모든 움직임이 끝난 후 헤드를 다시 잠글 수 있습니다.
    # reachy.head.block_joints()
    print("look_at 기능 예제를 종료합니다.")
``` 
