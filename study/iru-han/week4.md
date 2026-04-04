# 1. Reachy Mini의 카메라 시스템 이해
Reachy Mini는 두 개의 카메라(왼쪽 눈, 오른쪽 눈)를 통해 주변 환경을 인식할 수 있습니다. 이 카메라는 로봇이 물체를 추적하거나 환경과 상호작용하는 데 필수적인 시각 정보를 제공합니다.

## 1.1 카메라 사양 및 특징
위치: Reachy Mini의 헤드 부분, 각 눈 위치에 하나씩 장착되어 있습니다.
용도: 스테레오 비전을 통해 깊이 정보를 얻거나, 단안 비전으로 객체 인식 및 추적에 활용됩니다.
영상 스트림: Python SDK를 통해 실시간으로 카메라 영상 스트림에 접근할 수 있습니다. 영상은 일반적으로 NumPy 배열 형태로 제공됩니다.
1.2 Python SDK를 이용한 카메라 영상 취득
Reachy Mini의 Python SDK를 사용하면 카메라 영상 스트림에 쉽게 접근할 수 있습니다.

minimal.xml 파일 - 연보라색 박스 추가
```
<mujoco model="scene">
    <include file="../reachy_mini.xml" />
    <compiler meshdir="../assets" texturedir="../assets" />
    
    <option timestep="0.008" iterations="15" integrator="Euler">
        <flag multiccd="enable"/>
    </option>

    <visual>
        <headlight diffuse="0.6 0.6 0.6" ambient="0.3 0.3 0.3" specular="0 0 0" />
        <rgba haze="0 0 0 0" />
        <global azimuth="160" elevation="-20" offwidth="1280" offheight="720"/>
    </visual>

    <asset>
        <texture type="2d" name="groundplane" builtin="checker" mark="edge" rgb1="0.2 0.3 0.4" rgb2="0.1 0.2 0.3" width="300" height="300" />
        <material name="groundplane" texture="groundplane" texuniform="true" texrepeat="5 5" reflectance="0" />
        
        <material name="purple_material" rgba="0.8 0.6 1 1" reflectance="0" />
    </asset>

    <worldbody>
        <light pos="-0.5 0 3.5" dir="0 0 -1" directional="true" castshadow="false" />
        <geom name="floor" size="0 0 0.05" pos="0 0 -0.8" type="plane" material="groundplane" />

        <body name="table" pos="0.35 0 -0.8" euler="1.57 0 0">
            <geom name="table_top_collision" type="box" size="0.56 0.03 0.35" pos="0 0.77 0" friction="1 1 1" />
        </body>

        <body name="purple_box" pos="0.4 0 0.05">
            <geom name="purple_box_geom" type="box" size="0.04 0.04 0.04" material="purple_material" mass="0.5" friction="1 1 1"/>
            <joint name="purple_box_joint" type="free" />
        </body>
    </worldbody>
</mujoco>

```
<img width="640" height="816" alt="image" src="https://github.com/user-attachments/assets/610bedaf-faa4-40c1-8bb4-da32e4c9f7ba" />


예제: 카메라 영상 실시간으로 보기
```
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
            cv2.imshow('Reachy Mini Camera Feed', frame)
        else:
            # 프레임이 아직 준비되지 않았을 때
            print("프레임을 불러오는 중...")
            time.sleep(0.1)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
```
<img width="1274" height="743" alt="image" src="https://github.com/user-attachments/assets/919d627b-3af4-41dc-867b-1ddb5556dd6e" />


전처리 하기
```
import cv2
import numpy as np
import time
from reachy_mini import ReachyMini

# 4주차 2단계: OpenCV 영상 처리 및 색상 검출 실습
with ReachyMini() as mini:
    print("OpenCV 영상 처리 실습을 시작합니다. 'q' 키를 눌러 종료하세요.")
    
    while True:
        # [1.2] 영상 취득
        frame = mini.media.get_frame()
        if frame is None:
            continue

        # [2.2.1] 그레이스케일 변환: 처리 속도를 높이고 알고리즘 최적화를 위해 수행
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # [2.2.2] 블러링 (Blurring): 가우시안 블러를 통해 노이즈를 제거
        blurred_frame = cv2.GaussianBlur(frame, (5, 5), 0)

        # [2.2.3] 엣지 검출 (Edge Detection): Canny 알고리즘으로 객체의 윤곽 식별
        edges = cv2.Canny(gray_frame, 100, 200)

        # [2.2.4] 색상 기반 객체 검출 (HSV 마스크): 연보라색 상자 찾기
        # RGB보다 조명 변화에 강한 HSV 공간 사용
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 연보라색(Lavender)을 위한 HSV 범위 설정
        lower_lavender = np.array([130, 50, 50])
        upper_lavender = np.array([160, 255, 255])
        
        # 설정한 범위의 색상만 추출하여 마스크 생성
        mask = cv2.inRange(hsv_frame, lower_lavender, upper_lavender)
        # 원본 이미지와 마스크를 연산하여 해당 색상 객체만 표시
        res = cv2.bitwise_and(frame, frame, mask=mask)

        # 결과 창 표시
        cv2.imshow('1. Original Feed', frame)
        cv2.imshow('2. Grayscale', gray_frame)
        cv2.imshow('3. Edges (Canny)', edges)
        cv2.imshow('4. Lavender Object Mask', mask)
        cv2.imshow('5. Detected Object', res)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
```
<img width="946" height="796" alt="image" src="https://github.com/user-attachments/assets/f0cf1fa4-bd18-45f8-a13a-96727759c1c0" />
<img width="1250" height="712" alt="image" src="https://github.com/user-attachments/assets/7fdb066f-e632-4b36-859e-9784254f4fbb" />

그레이스케일 후 엣지검출
<img width="1265" height="733" alt="image" src="https://github.com/user-attachments/assets/301c0725-4755-4a8d-9411-ed9604a895b5" />
<img width="1270" height="737" alt="image" src="https://github.com/user-attachments/assets/587c41c1-c736-4947-b948-5f8749052cac" />

가우시안 블러
<img width="1273" height="736" alt="image" src="https://github.com/user-attachments/assets/f21e7b53-3100-4744-8d42-d6bb7f35d43e" />

색상검출
<img width="1274" height="744" alt="image" src="https://github.com/user-attachments/assets/3699a79b-5f2f-444f-aad6-c51686ea9066" />
<img width="1268" height="742" alt="image" src="https://github.com/user-attachments/assets/6a2ba928-08ac-46c0-99b4-aa75cb02b164" />


look_at 예제
```
import cv2
import numpy as np
import time
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

with ReachyMini() as mini:
    # 발표용 창을 아예 두 개로 분리하여 시연하세요. (전문성 어필)
    cv2.namedWindow('ROBOT_VIEW', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('ROBOT_VIEW', 400, 300)
    
    print("🔥 프레임 동기화 모드 가동! 시연을 시작합니다.")
    
    while True:
        frame_data = mini.media.get_frame()
        if frame_data is None: continue

        # [비책 1] 가져오자마자 copy()해서 시뮬레이션 버퍼와 인연을 끊습니다.
        # 이렇게 해야 화면 찢어짐(Tearing)이 방지됩니다.
        frame = frame_data.copy()

        # [비책 2] 연산은 아주 작게 (160p) 하여 CPU를 아낍니다.
        small = cv2.resize(frame, (160, 90), interpolation=cv2.INTER_NEAREST)
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([120, 30, 30]), np.array([170, 255, 255]))
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest) > 5:
                M = cv2.moments(largest)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])

                    # 시선 추적 실행
                    roll, pitch = (cx/160 - 0.5) * -75, (cy/90 - 0.5) * 55
                    mini.set_target(head=create_head_pose(roll=roll, pitch=pitch))

                    # 결과물에만 표시 (원본 훼손 방지)
                    cv2.circle(frame, (int(cx * frame.shape[1]/160), int(cy * frame.shape[0]/90)), 20, (0, 255, 0), -1)

        # [비책 3] imshow 대기 시간을 40ms로 늘려 윈도우 주사율과 맞춥니다.
        cv2.imshow('ROBOT_VIEW', frame)
        
        if cv2.waitKey(40) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
```
https://github.com/user-attachments/assets/df373a88-f4ea-4835-a0f8-8dccdb0ec951


roll, pitch = (cx/160 - 0.5) * -75, (cy/90 - 0.5) * 55<br/><br/>

1단계: 0~1 사이의 비율로 만들기 (cx / 160)<br/>
의미: 현재 상자가 전체 화면 너비(160px) 중 어디쯤 있는지 비율로 나타냅니다.<br/>
예: 상자가 맨 오른쪽에 있으면 160/160 = 1이 되고, 정중앙에 있으면 80/160 = 0.5가 됩니다.<br/>
                    
2단계: 중앙을 0으로 만들기 (- 0.5)<br/>
의미: 이미지의 왼쪽 끝을 -0.5, 오른쪽 끝을 +0.5로 만들어 화면 정중앙을 0으로 맞춥니다.<br/>
이유: 로봇 머리는 정면(0도)을 기준으로 좌우로 움직여야 하기 때문입니다.<br/>
                    
3단계: 실제 각도(Degree)로 뻥튀기 (* -75, * 55)<br/>
의미: 위에서 구한 -0.5 ~ +0.5 사이의 값에 로봇이 움직일 수 있는 최대 회전 범위를 곱해줍니다.<br/>
결과: 정규화된 값 0.5에 -75를 곱하면 약 -37.5도 만큼 고개를 돌리라는 명령이 됩니다.<br/>

웹캠으로 파란색 추적하기
```
import cv2
import numpy as np
import time
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose 

def pixel_to_angle(cx, cy, img_w, img_h):
    # 정규화 좌표 계산: 중앙을 0으로 맞춤
    nx = (cx / img_w) - 0.5
    ny = (cy / img_h) - 0.5
    # 민감도: 좌우 약 70도, 상하 약 50도 범위
    return nx * -70, ny * 50 

with ReachyMini(media_backend="no_media") as mini:
    print("파란색 타겟 추적")
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret: break

        # 1. HSV 색공간으로 변환
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 2. 파란색 범위 설정 (일반적인 파란색 영역)
        # H(색상): 100~130 범위가 파란색입니다.
        # S(채도): 100 이상 (너무 흐린 파란색 제외)
        # V(명도): 100 이상 (너무 어두운 파란색 제외)
        lower_blue = np.array([100, 100, 100])
        upper_blue = np.array([130, 255, 255]) 
        
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # 3. 물체 중심점 찾기
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest = max(contours, key=cv2.contourArea)
            # 노이즈를 방지하기 위해 일정 크기 이상의 물체만 인식 (면적 1000)
            if cv2.contourArea(largest) > 1000:
                M = cv2.moments(largest)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    img_h, img_w = frame.shape[:2]
                    roll, pitch = pixel_to_angle(cx, cy, img_w, img_h)

                    # 4. 로봇 제어 명령 전송
                    mini.set_target(head=create_head_pose(roll=roll, pitch=pitch))

                    # 화면 표시: 물체 테두리와 중심점 그리기
                    cv2.drawContours(frame, [largest], -1, (255, 0, 0), 2)
                    cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)
                    cv2.putText(frame, "Blue Object Detected", (cx-20, cy-20), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # 결과 화면 출력
        cv2.imshow('Reachy Mini - Blue Tracking', frame)
        
        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
cv2.destroyAllWindows()
```

## 1. 좌표 변환 함수: pixel_to_angle
정규화 (Normalization): <br/>
(cx / img_w) - 0.5이미지 좌측 상단이 (0,0)인 좌표계를 이미지 중앙이 (0,0)이 되도록 바꿉니다. <br/>
결과값은 -0.5(왼쪽 끝)에서 +0.5(오른쪽 끝) 사이가 됩니다. <br/>

스케일링 (Scaling):  <br/>
nx * -70로봇 머리가 움직일 수 있는 실제 범위(Gain)를 곱합니다. <br/>
마이너스(-)를 곱한 이유: 카메라 영상의 우측 방향(+)이 로봇 관절의 기준 방향(-)과 반대 <br/>

## 2. 정보 추출: 컨투어(Contours)와 모멘트(Moments)
이진화된 마스크에서 "물체"라는 의미 있는 데이터를 뽑아내는 단계입니다. <br/>
findContours: 흰색 덩어리들의 외곽선을 찾습니다. <br/>
max(contours, key=cv2.contourArea): 화면에 잡히는 수많은 파란색 노이즈 중 가장 면적이 큰 것 하나만 진짜 타겟으로 결정합니다. <br/>

## 3. 로봇 제어: set_target과 피드백 루프추출된 정보를 물리적인 움직임으로 바꿉니다.
mini.set_target(...): 계산된 각도를 로봇에게 전송합니다.<br/>
create_head_pose: Roll(좌우 회전), Pitch(상하 회전) 값을 로봇이 이해할 수 있는 포즈 객체로 포장합니다.<br/>
제어 루프: 이 과정이 while True 문 안에서 무한히 반복되며, "물체 발견 -> 중심 계산 -> 고개 이동"이라는 폐루프 제어(Closed-loop control) 시스템을 완성합니다.<br/>

https://github.com/user-attachments/assets/80ad7809-03d5-47e6-b0ed-64396ead32f3
https://github.com/user-attachments/assets/37b382d3-0fee-48ce-a67b-2424f2bfa9cf



