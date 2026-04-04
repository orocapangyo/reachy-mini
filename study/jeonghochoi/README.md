# Unity에서 로봇 모델 움직임 구현하기

[스크린캐스트 2025년 09월 11일 18시 11분 21초.webm](https://github.com/user-attachments/assets/bc357187-e2af-4f74-8c04-1c81e05bec8a)

## 로보틱스 관련 세팅
<img width="1280" height="730" alt="image (1)" src="https://github.com/user-attachments/assets/bb863787-7305-4876-b5ce-0345ae09f19e" />

(Window - package Management - Package Manager)

<img width="886" height="609" alt="image (2)" src="https://github.com/user-attachments/assets/4e29dc9f-d341-4cc4-a229-497d63b075c6" />

## 3가지 인포트하기

1. ROS TCP Connector
https://github.com/Unity-Technologies/ROS-TCP-Connector.git?path=/com.unity.robotics.ros-tcp-connector

2 .Unity Robotics Visualizations
https://github.com/Unity-Technologies/ROS-TCP-Connector.git?path=/com.unity.robotics.visualizations

3. URDF Importer
https://github.com/Unity-Technologies/URDF-Importer.git?path=/com.unity.robotics.urdf-importer

### 로봇 세팅

Robotics - ROS Setting

protocol Ros2로 변경

<img width="468" height="671" alt="image (3)" src="https://github.com/user-attachments/assets/bd115533-ee91-4956-bfd7-50dab72524a3" />

---

#### Ros2와 연동하기 위한 추가 설명자료
https://pnltoen.tistory.com/entry/%EC%9A%B0%EB%B6%84%ED%88%AC%EC%97%90-Unity-Robotics-%EC%84%A4%EC%B9%98%ED%95%98%EA%B8%B0-Setup

##### 아래의 링크에서 ROS2 브랜치 소스 설치(~/robot_ws/src) 및 빌드

https://github.com/Unity-Technologies/ROS-TCP-Endpoint
colcon build --packages-select ros_tcp_endpoint

##### endpoint 노드 실행

ros2 launch ros_tcp_endpoint endpoint.py

#### ROSConnection 추가

유니티에 아무 오브젝트 하나 만들고, 오브젝트에 ROSConnection.cs 스크립트를 컴포넌트로 추가

Cube → `Add Component` → `ROSConnection` 검색 → 추가 가능해야 함

`Assets > ROS-TCP-Connector > Scripts > ROSConnection.cs` 경로에 있음


##### 테스트용 메세지 퍼블리셔 추가

- Unity에서 `Project` 창으로 이동
- `Assets/Scripts/` 폴더가 없다면 `Scripts` 폴더 생성
- `Scripts` 폴더에서 오른쪽 클릭 → **Create > C# Script**
- 이름을 `StringPublisher`로 지정

생성된 `StringPublisher.cs` 에 다음 코드 작성 (파일안에있음)

모델에  `Add Component` 하여

위 스크립트도 컴포넌트로 추가하기


game창에서 상단 중앙의 플레이버튼 실행

##### 새로운 터미널에서 유니티가 발행하는 토픽 구독
ros2 topic echo /unity_chatter

통신이 완료 된 모습
<img width="732" height="684" alt="image (4)" src="https://github.com/user-attachments/assets/5b1e6cc0-fbf6-447f-ae1a-c7121a9e6fd7" />

---


### 블렌더 파일 유니티 오브젝트로 넣기

blender에서 File - Export - FBX파일로 저장

<img width="1920" height="1199" alt="image (1)" src="https://github.com/user-attachments/assets/2fc9174b-11fd-4610-b37c-9313a03f88bc" />




이후 유니티 프로젝트에 추가 후, 씬에 삽입

<img width="1848" height="1032" alt="image (2)" src="https://github.com/user-attachments/assets/b5fd9eaf-29e4-4021-bb70-b9e9d6c55827" />

### 안태나와 머리에 움직임을 부여

[스크린캐스트 2025년 09월 11일 18시 09분 50초.webm](https://github.com/user-attachments/assets/11b4a529-9672-4629-a344-d3cac37e9feb)



