# Reachy Mini 개발 환경 설정 및 실행 가이드

## 1. 파이썬 설치
3.14 로 설치하면 하단같이 numpy 에러가 뜬다. 그래서 일단 12.9로 설치.

https://www.python.org/downloads/release/python-3129/

Python Release Python install manager 26.0

The official home of the Python Programming Language

www.python.org


런타임 라이브러리 설치

https://learn.microsoft.com/ko-kr/cpp/windows/latest-supported-vc-redist?view=msvc-170

지원되는 최신 Visual C++ 재배포 가능 패키지 다운로드

이 문서에서는 최신 Visual C++ 재배포 가능 패키지에 대한 다운로드 링크를 제공합니다.

learn.microsoft.com


## 3. 개발 환경 설정 (Windows 기준)
가장 먼저 터미널(PowerShell 또는 CMD)을 열고 아래 명령어를 입력하세요.

### Python 가상환경 생성 및 활성화
# 권한 설정 - Y 또는 A 누르고 해결
# "실행 규칙을 변경하시겠습니까?" 라고 물어보면 Y 또는 A 누르고 엔터
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

cd C:\reachy

# 프로젝트를 진행할 폴더로 이동 후
python -m venv venv

# 가상환경 활성화 (윈도우 핵심!)
.\venv\Scripts\activate
Tip: 활성화되면 터미널 앞에 (reachy_env)라는 표시가 뜹니다.

### SDK 및 시뮬레이터 설치
윈도우에서는 udev 설정(리눅스 전용)이 필요 없습니다. 바로 설치로 넘어갑니다.

python.exe -m pip install --upgrade pip

pip install reachy-mini
pip install reachy-mini[mujoco]

# 위 명령어가 안되면
C:\reachy\venv\Scripts\python.exe -m pip install reachy-mini reachy-mini[mujoco]


## 2. 시뮬레이션 환경 실행 (MuJoCo)
과제 제출을 위해 가장 중요한 부분입니다. 시뮬레이터를 먼저 띄워야 코드가 작동합니다.

### 데몬(Daemon) 실행
새 터미널을 하나 더 열거나(가상환경 활성화 필수), 기존 터미널에서 아래 명령어를 입력하세요.

reachy-mini-daemon --sim --deactivate-audio

성공 시: MuJoCo 시뮬레이터 창이 뜨면서 Reachy Mini 로봇 모델이 보일 겁니다. 이 화면을 캡처해서 과제로 제출하세요!


## 3. 첫 번째 프로그램 실행
시뮬레이터가 켜진 상태에서, 메모장이나 VS Code를 열어 아래 코드를 test.py로 저장한 뒤 실행합니다.

새 터미널에서 가상환경을 활성화합니다.

cd C:\reachy
.\venv\Scripts\activate

이 코드를 복사해서 test.py에 붙여넣으세요.

```
from reachy_mini import ReachyMini

with ReachyMini() as mini:
    print("--- 1주차 과제 확인 ---")
    print(f"로봇 모델: {mini.robot_name} | 연결 성공!")
    
    # 데이터 구조: ([몸체 관절들], [안테나 관절들])
    all_data = mini.get_current_joint_positions()
    print(f"데이터 구조: {all_data}")
    
    if all_data and len(all_data) >= 1:
        body_joints = all_data[0]     # 첫 번째 리스트 (몸체)
        antenna_joints = all_data[1]  # 두 번째 리스트 (안테나)

        print("\n[메인 관절 상태]")
        for i, pos in enumerate(body_joints):
            print(f"관절 {i+1:02d}: {pos:8.4f} rad")

        print("\n[안테나 관절 상태]")
        for i, pos in enumerate(antenna_joints):
            print(f"안테나 {i+1}: {pos:8.4f} rad")
    else:
        print("데이터를 불러오지 못했습니다.")
        
    print("\n--- 과제 완료! 이 화면과 시뮬레이터를 캡처하세요 ---")
```

실행 명령어: <br/>
python test.py

<img width="1280" height="698" alt="image" src="https://github.com/user-attachments/assets/bb509e8a-1830-41c3-b33d-0ffdaee18bee" />

