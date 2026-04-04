## 4주차: 센서 활용 - 카메라

### 학습 목표

- 카메라 영상 취득 및 처리
- OpenCV를 활용한 영상 처리
- look_at 기능 구현

---

### 1. Reachy Mini의 카메라 시스템 이해

Reachy Mini는 두 개의 카메라(왼쪽 눈, 오른쪽 눈)를 통해 주변 환경을 인식할 수 있습니다. 이 카메라는 로봇이 물체를 추적하거나 환경과 상호작용하는 데 필수적인 시각 정보를 제공합니다.

#### 1.1 카메라 사양 및 특징

*   **위치**: Reachy Mini의 헤드 부분, 각 눈 위치에 하나씩 장착되어 있습니다.
*   **용도**: 스테레오 비전을 통해 깊이 정보를 얻거나, 단안 비전으로 객체 인식 및 추적에 활용됩니다.
*   **영상 스트림**: Python SDK를 통해 실시간으로 카메라 영상 스트림에 접근할 수 있습니다. 영상은 일반적으로 `NumPy` 배열 형태로 제공됩니다.

#### 1.2 Python SDK를 이용한 카메라 영상 취득

Reachy Mini의 Python SDK를 사용하면 카메라 영상 스트림에 쉽게 접근할 수 있습니다.

**예제: 카메라 영상 실시간으로 보기**

```python
import time
import cv2
from reachy_mini_sdk import ReachyMini

# Reachy Mini 인스턴스 생성 (로봇의 IP 주소로 대체하세요)
# reachy = ReachyMini(host='192.168.x.x') 
reachy = ReachyMini(host='localhost') # 시뮬레이션 또는 로컬 테스트 시

print("카메라 스트림을 시작합니다. 'q' 키를 눌러 종료하세요.")

try:
    while True:
        # 왼쪽 카메라에서 이미지 가져오기
        # .left_image 스트림은 비동기적으로 이미지를 제공합니다.
        # 최신 이미지를 얻기 위해 get_image()를 사용할 수도 있습니다.
        frame = reachy.head.get_image() # get_image()는 새로운 이미지가 준비될 때까지 기다립니다.

        if frame is not None:
            # OpenCV를 사용하여 창에 이미지 표시
            cv2.imshow('Reachy Mini Camera Feed (Left)', frame)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"오류 발생: {e}")
finally:
    # 모든 OpenCV 창 닫기
    cv2.destroyAllWindows()
    print("카메라 스트림을 종료합니다.")
```

**설명:**
*   `ReachyMini(host='...')`: Reachy Mini 로봇에 연결하기 위한 객체를 생성합니다. `host`에는 로봇의 IP 주소를 입력해야 합니다. 시뮬레이션 환경에서는 `localhost`를 사용할 수 있습니다.
*   `reachy.head.get_image()`: Reachy Mini 헤드의 카메라로부터 현재 프레임(이미지)을 가져옵니다. 이 함수는 이미지가 `NumPy` 배열 형태로 반환됩니다.
*   `cv2.imshow()`: OpenCV 라이브러리의 함수로, 이미지를 화면에 표시하는 데 사용됩니다.
*   `cv2.waitKey(1)`: 1ms 동안 키 입력을 기다립니다. `0xFF == ord('q')`는 'q' 키가 눌렸는지 확인합니다.

### 2. OpenCV를 활용한 영상 처리

OpenCV(Open Source Computer Vision Library)는 실시간 컴퓨터 비전 애플리케이션 개발을 위한 오픈 소스 라이브러리입니다. 영상 처리, 객체 인식, 머신러닝 등 다양한 기능을 제공합니다.

#### 2.1 OpenCV 설치

Python 환경에서 OpenCV를 설치하는 가장 쉬운 방법은 `pip`를 사용하는 것입니다.

```bash
pip install opencv-python numpy
```

#### 2.2 기본적인 영상 처리 기술

Reachy Mini 카메라에서 얻은 영상을 OpenCV를 사용하여 다양하게 처리할 수 있습니다.

**2.2.1 그레이스케일 변환**

컬러 이미지를 흑백 이미지로 변환하여 처리 속도를 높이거나 특정 알고리즘에 적합한 형태로 만듭니다.

```python
# ... (카메라 영상 취득 코드 이어서)
        if frame is not None:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cv2.imshow('Grayscale Feed', gray_frame)
            cv2.imshow('Reachy Mini Camera Feed (Left)', frame)
# ...
```

**2.2.2 블러링 (Blurring)**

이미지의 노이즈를 제거하거나 세부 정보를 부드럽게 만들어 특징 추출에 용이하게 합니다. 가우시안 블러가 일반적으로 사용됩니다.

```python
# ... (카메라 영상 취득 코드 이어서)
        if frame is not None:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred_frame = cv2.GaussianBlur(frame, (5, 5), 0) # (5,5)는 커널 크기
            cv2.imshow('Blurred Feed', blurred_frame)
            cv2.imshow('Reachy Mini Camera Feed (Left)', frame)
# ...
```

**2.2.3 엣지 검출 (Edge Detection)**

이미지의 경계를 찾아 객체의 윤곽을 식별하는 데 사용됩니다. Canny 엣지 검출이 대표적입니다.

```python
# ... (카메라 영상 취득 코드 이어서)
        if frame is not None:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray_frame, 100, 200) # 100, 200은 임계값
            cv2.imshow('Edges', edges)
            cv2.imshow('Reachy Mini Camera Feed (Left)', frame)
# ...
```

**2.2.4 색상 기반 객체 검출 (HSV 마스크)**

특정 색상을 가진 객체를 이미지에서 분리하는 데 유용합니다. RGB 대신 HSV(Hue, Saturation, Value) 색상 공간을 사용하면 색상 변화에 더 강인하게 반응합니다.

```python
# ... (카메라 영상 취득 코드 이어서)
        if frame is not None:
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # 초록색 객체를 검출하기 위한 HSV 범위 (예시)
            lower_green = (35, 100, 100)
            upper_green = (85, 255, 255)

            # HSV 이미지에서 지정된 범위의 색상만 추출하여 마스크 생성
            mask = cv2.inRange(hsv_frame, lower_green, upper_green)

            # 원본 이미지와 마스크를 AND 연산하여 초록색 객체만 표시
            res = cv2.bitwise_and(frame, frame, mask=mask)

            cv2.imshow('Green Object Mask', mask)
            cv2.imshow('Green Object Detected', res)
            cv2.imshow('Reachy Mini Camera Feed (Left)', frame)
# ...
```

### 3. Reachy Mini `look_at` 기능 구현

`look_at` 기능은 Reachy Mini가 특정 3D 공간 좌표를 바라보도록 헤드를 움직이는 강력한 기능입니다. 이는 로봇이 특정 사람이나 물체에 시선을 고정하게 하여 자연스러운 상호작용을 가능하게 합니다.

#### 3.1 `reachy.head.look_at()` 메서드

`look_at()` 메서드는 Reachy Mini 헤드의 움직임을 제어하여 지정된 3D 점을 바라보게 합니다.

**메서드 시그니처:**
`reachy.head.look_at(x: float, y: float, z: float, duration: float = 1.0, wait: bool = True)`

*   `x, y, z`: 로봇의 기준 좌표계(World Frame)에서 바라볼 대상의 3D 좌표 (단위: 미터).
*   `duration`: 헤드가 목표 지점으로 이동하는 데 걸리는 시간 (단위: 초).
*   `wait`: `True`인 경우, 움직임이 완료될 때까지 함수가 블록됩니다. `False`인 경우, 움직임이 시작된 후 즉시 반환됩니다.

#### 3.2 좌표계 이해 (World Frame)

`look_at` 기능에서 사용하는 `x, y, z` 좌표는 Reachy Mini 로봇의 'World Frame'을 기준으로 합니다.

*   **원점 (0,0,0)**: 일반적으로 로봇의 몸체 중앙 하단 또는 로봇이 서 있는 지면의 중앙을 기준으로 설정됩니다. Reachy Mini 문서에서 정확한 World Frame 정의를 확인하는 것이 중요합니다.
*   **X축**: 로봇의 앞쪽 방향
*   **Y축**: 로봇의 왼쪽 또는 오른쪽 방향
*   **Z축**: 로봇의 위쪽 방향

#### 3.3 예제: 특정 3D 공간 좌표 바라보기

Reachy Mini가 특정 고정된 3D 위치를 바라보게 하는 예제입니다.

```python
import time
from reachy_mini_sdk import ReachyMini

# Reachy Mini 인스턴스 생성
# reachy = ReachyMini(host='192.168.x.x')
reachy = ReachyMini(host='localhost')

# 헤드의 잠금을 해제하여 움직임을 허용합니다.
reachy.head.unblock_joints()

print("Reachy Mini가 여러 지점을 바라봅니다.")

try:
    # 1. (0.5, 0, 0.3) 지점 (로봇 전방 50cm, 높이 30cm) 바라보기
    print("Point 1: (0.5, 0, 0.3)")
    reachy.head.look_at(x=0.5, y=0, z=0.3, duration=2.0)
    time.sleep(2)

    # 2. (0.3, 0.2, 0.5) 지점 (로봇 전방 30cm, 오른쪽 20cm, 높이 50cm) 바라보기
    print("Point 2: (0.3, 0.2, 0.5)")
    reachy.head.look_at(x=0.3, y=0.2, z=0.5, duration=2.0)
    time.sleep(2)

    # 3. (0.3, -0.2, 0.5) 지점 (로봇 전방 30cm, 왼쪽 20cm, 높이 50cm) 바라보기
    print("Point 3: (0.3, -0.2, 0.5)")
    reachy.head.look_at(x=0.3, y=-0.2, z=0.5, duration=2.0)
    time.sleep(2)

except Exception as e:
    print(f"오류 발생: {e}")
finally:
    # 모든 움직임이 끝난 후 헤드를 다시 잠글 수 있습니다.
    # reachy.head.block_joints()
    print("look_at 기능 예제를 종료합니다.")
```

**설명:**
*   `reachy.head.unblock_joints()`: Reachy Mini의 관절은 기본적으로 '잠금' 상태일 수 있습니다. 움직임을 시작하기 전에 이 함수를 호출하여 관절 잠금을 해제해야 합니다.
*   `time.sleep()`: 움직임 사이의 지연 시간을 주어 각 목표 지점을 명확히 볼 수 있도록 합니다.

#### 3.4 OpenCV와 `look_at` 연동 (심화)

OpenCV를 통해 이미지에서 객체의 2D 좌표를 얻은 후, 이를 Reachy Mini의 3D World Frame 좌표로 변환하여 `look_at` 기능과 연동할 수 있습니다. 2D 이미지 좌표를 3D 월드 좌표로 변환하는 것은 복잡한 과정이며, 카메라 캘리브레이션, 핀홀 카메라 모델, 기하학적 변환 등의 지식이 필요합니다.

**기본 아이디어:**
1.  OpenCV로 카메라 영상에서 관심 객체(예: 얼굴, 특정 색상 공)의 중심 2D 좌표를 검출합니다.
2.  검출된 2D 좌표와 카메라의 내부 파라미터(초점 거리, 주점 등), 그리고 로봇과 카메라 간의 외부 파라미터(회전, 이동)를 사용하여 해당 객체의 3D 월드 좌표를 추정합니다.
3.  추정된 3D 월드 좌표를 `reachy.head.look_at()` 메서드에 전달하여 Reachy Mini가 해당 객체를 바라보도록 합니다.

이 부분은 고급 주제이므로, 여기서는 개념만 설명하고 간단한 예시 코드를 제시합니다. 실제 구현에서는 더 많은 고려사항이 필요합니다.

**예제: OpenCV로 검출한 객체 중심을 바라보기 (개념 코드)**

```python
import time
import cv2
from reachy_mini_sdk import ReachyMini
# from your_module import convert_2d_to_3d_world_coords # 2D to 3D 변환 함수가 필요합니다.

# Reachy Mini 인스턴스 생성
# reachy = ReachyMini(host='192.168.x.x')
reachy = ReachyMini(host='localhost')
reachy.head.unblock_joints()

# Haar Cascade를 이용한 얼굴 검출기 로드 (OpenCV 설치 시 동봉)
# XML 파일의 경로를 정확히 지정해야 합니다.
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

print("얼굴을 인식하여 Reachy Mini가 바라보도록 합니다. 'q' 키를 눌러 종료하세요.")

try:
    while True:
        frame = reachy.head.get_image()

        if frame is not None:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray_frame, 1.1, 4)

            for (x, y, w, h) in faces:
                # 검출된 얼굴에 사각형 그리기
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

                # 얼굴의 중심 2D 좌표
                center_x_2d = x + w // 2
                center_y_2d = y + h // 2

                # 2D 좌표를 3D World Frame 좌표로 변환하는 함수 (사용자 구현 필요)
                # 이 함수는 카메라 캘리브레이션 정보 등을 활용해야 합니다.
                # 임시로 더미 3D 좌표를 사용합니다.
                # target_3d_x, target_3d_y, target_3d_z = convert_2d_to_3d_world_coords(center_x_2d, center_y_2d, frame.shape)
                # 여기서는 간단한 예시를 위해 고정된 깊이와 이미지 중심으로부터의 상대적 위치를 사용합니다.
                
                # 이미지 중앙을 (0,0)으로 가정하고 픽셀당 미터 변환 비율을 대략적으로 사용 (매우 단순화된 예시)
                img_h, img_w = frame.shape[:2]
                
                # 이미지 중심을 기준으로 한 픽셀 오프셋
                pixel_offset_x = center_x_2d - img_w / 2
                pixel_offset_y = center_y_2d - img_h / 2
                
                # 가상의 "픽셀-to-미터" 변환 비율. 실제 구현에서는 카메라 캘리브레이션으로 구해야 함.
                # Reachy Mini의 head-base frame에 대한 상대적인 위치를 고려해야 합니다.
                # 예를 들어, 0.001 미터/픽셀 이라는 가상의 비율로 2D 픽셀을 3D World Frame Y, Z 축으로 매핑
                # X (깊이)는 고정된 값 (예: 0.5m)으로 가정
                
                # Reachy Mini의 World Frame 기준:
                # X: 로봇 전방
                # Y: 로봇 왼쪽 (+) / 오른쪽 (-)
                # Z: 로봇 상단 (+) / 하단 (-)
                
                # 카메라 이미지는 일반적으로 Y축이 오른쪽, Z축이 아래쪽으로 증가.
                # 로봇 World Frame으로 변환 시, 이미지의 X 픽셀 오프셋은 World Frame의 Y축에,
                # 이미지의 Y 픽셀 오프셋은 World Frame의 -Z축에 매핑될 수 있습니다.
                
                distance_to_face = 0.8 # 얼굴까지의 예상 거리 (미터), 실제로는 깊이 추정 필요
                
                # 이미지 픽셀 오프셋을 World Frame 좌표로 변환
                # World Frame (x, y, z)
                # x: depth (가장 앞에 있는 사람이 0.5m 거리에 있다고 가정)
                # y: horizontal offset (왼쪽으로 갈수록 양수)
                # z: vertical offset (위로 갈수록 양수)
                
                # Reachy Mini의 헤드 카메라가 대략 월드 프레임의 z=0.5m 정도에 있다고 가정
                # 그리고 헤드 자체의 look_at은 헤드 카메라 프레임을 기준으로 월드 프레임을 계산함
                # 그러므로 카메라 이미지 중심에서 픽셀 오프셋을 월드 프레임으로 대략 매핑 (간단화)
                
                # 이 예제는 매우 간소화되었으며, 정확한 2D-to-3D 변환은 카메라 캘리브레이션이 필요합니다.
                # 여기서는 단순히 이미지 중심으로부터의 상대적 위치를 기반으로 look_at을 테스트합니다.
                
                # World Frame 기준 (로봇 앞 0.5m, 수평/수직 offset 적용)
                # 카메라의 Y축 움직임(좌우)은 로봇 World Frame의 Y축(좌우)에 해당
                # 카메라의 X축 움직임(상하)은 로봇 World Frame의 Z축(상하)에 해당 (단, 방향 반전 필요)
                
                # 픽셀당 미터 변환 계수 (예시 값, 실제는 캘리브레이션 필요)
                pixel_to_meter_ratio_x = 0.001 # 1픽셀당 0.001미터 (가로)
                pixel_to_meter_ratio_y = 0.001 # 1픽셀당 0.001미터 (세로)
                
                # 로봇 기준점으로부터의 x, y, z
                # x (깊이): 고정된 값 또는 깊이 센서로 측정
                target_x = distance_to_face 
                
                # y (좌우): 이미지 중심으로부터의 수평 편차 (왼쪽이 +y)
                target_y = -pixel_offset_x * pixel_to_meter_ratio_x # 카메라 x 오프셋은 월드 y에 영향을 줍니다.
                
                # z (상하): 이미지 중심으로부터의 수직 편차 (위쪽이 +z)
                target_z = -pixel_offset_y * pixel_to_meter_ratio_y + 0.5 # 카메라 y 오프셋은 월드 z에 영향을 줍니다. (0.5는 Reachy 머리 대략적인 높이)

                print(f"Detected Face at 2D ({center_x_2d}, {center_y_2d}), Estimated 3D ({target_x:.2f}, {target_y:.2f}, {target_z:.2f})")
                reachy.head.look_at(x=target_x, y=target_y, z=target_z, duration=0.5)
                break # 가장 큰 얼굴 하나만 추적

            cv2.imshow('Reachy Mini Camera Feed with Face Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"오류 발생: {e}")
finally:
    cv2.destroyAllWindows()
    # reachy.head.block_joints()
    print("OpenCV와 look_at 연동 예제를 종료합니다.")
```

**중요 사항:**
*   위의 2D-to-3D 변환 예제는 매우 단순화된 개념 코드입니다. 실제 로봇에서 정확한 `look_at`을 구현하려면 Reachy Mini의 카메라 캘리브레이션 데이터와 World Frame에 대한 정확한 이해, 그리고 3D 좌표 변환 라이브러리(예: Placo, SciPy의 Rotation 등) 사용이 필요합니다.
*   `face_cascade` XML 파일의 경로는 시스템마다 다를 수 있으니, `cv2.data.haarcascades`를 사용하여 OpenCV 설치 경로 내의 기본 경로를 참조하는 것이 좋습니다.

### 4. 심화 학습 및 도전 과제

*   **동적 객체 추적**: `look_at` 기능과 OpenCV 객체 추적 알고리즘(예: Mean-Shift, CAMShift, CSRT)을 결합하여 움직이는 물체를 실시간으로 계속 바라보도록 시스템을 구축해 보세요.

#### 객체 추적 알고리즘 비교

| 특성 | Mean-Shift | CAMShift | CSRT |
|------|------------|----------|------|
| **알고리즘 원리** | 색상 히스토그램 기반 밀도 추정 | Mean-Shift + 적응적 윈도우 크기 | 판별적 상관 필터 (DCF) |
| **속도** | ⭐⭐⭐ 매우 빠름 | ⭐⭐⭐ 매우 빠름 | ⭐⭐ 보통 |
| **정확도** | ⭐ 낮음 | ⭐⭐ 보통 | ⭐⭐⭐ 높음 |
| **크기 변화 대응** | ❌ 불가능 | ✅ 가능 (자동 조절) | ✅ 가능 |
| **회전 대응** | ❌ 불가능 | ✅ 부분적 가능 | ✅ 가능 |
| **가림 (Occlusion) 대응** | ❌ 취약 | ❌ 취약 | ⭐⭐ 보통 |
| **OpenCV 함수** | `cv2.meanShift()` | `cv2.CamShift()` | `cv2.TrackerCSRT_create()` |
| **용도** | 단순/빠른 추적 | 크기 변화 있는 객체 | 정밀 추적 필요 시 |
| **초기화** | ROI + 히스토그램 | ROI + 히스토그램 | ROI만 필요 |
| **실시간 적합성** | ⭐⭐⭐ 최적 | ⭐⭐⭐ 최적 | ⭐⭐ 적합 |
*   **스테레오 비전**: Reachy Mini의 두 카메라를 활용하여 스테레오 매칭을 통해 객체의 실제 깊이 정보를 얻고, 이를 `look_at` 기능에 적용해 보세요.
*   **커스텀 객체 인식**: 미리 훈련된 모델(예: YOLO, SSD)이나 템플릿 매칭을 사용하여 특정 객체를 인식하고 추적하는 기능을 구현해 보세요.
*   **사용자 인터페이스**: Tkinter, PyQt 또는 Streamlit과 같은 라이브러리를 사용하여 카메라 영상과 로봇 제어 상태를 시각적으로 보여주는 간단한 GUI를 만들어 보세요.

---
