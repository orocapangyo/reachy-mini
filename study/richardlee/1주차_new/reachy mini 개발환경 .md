# reachy mini 개발환경

## 1.Reachy Mini Platform

**Choose your platform to access the specific guide:**

|**🤖 Reachy Mini (Wireless)**|**🔌 Reachy Mini Lite**|**💻 Simulation**|
|-|-|-|
|The full autonomous experience.Raspberry Pi 4 + Battery + WiFi.|The developer version.USB connection to your computer.|No hardware required.Prototype in MuJoCo.|
||||

![시뮬레이션과 실제 로봇 비교.png](./시뮬레이션과_실제_로봇_비교.png)

# \*\*\*\*

## 2-1. Python환경설치

**Git LFS (Large File Storage):**

* 3D 모델(메쉬 파일)을 다운로드하기 위해 필수입니다.
* [git-lfs.com](https://git-lfs.com/)에서 윈도우용 인스톨러를 받아 설치하세요.
* 설치 후 터미널에서 `git lfs install`을 한 번 입력해 줍니다

UV 통한 파이썬 설치 가상환경 설정

```
# 1. uv 설치 (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. 프로젝트 디렉토리 생성
mkdir reachy\\\_mini\\\_project
cd reachy\\\_mini\\\_project

# 3. Python 3.12 환경 생성
uv venv --python 3.12

# 4. 가상환경 활성화 (Windows)
.venv\\\\Scripts\\\\activate

# You should see (reachy\\\_mini\\\_env) at the start of your command line prompt!

```

### **2-2. Reachy Mini SDK , Mujoco설치**

> \\\*\\\*\\\*Recommended for most users - Just want to control your robot? This is for you!\\\*\\\*\\\*
> 

실물 로봇 실행 할 경우

```
uv pip install "reachy-mini"
```

Simulation 경우

```
uv pip install "reachy-mini\\\[mujoco]"
```

## 2-3. 로봇 서버 러닝 (Daemon)

The **Daemon** is a background service that handles the low-level communication with motors and sensors. It must be running for your code to work.

# reachy-mini는 ROS가 아니라 gRPC 기반 Deamon이 제어 하는 구조

```
reachy-mini-daemon 
```

* **For Simulation (No robot needed)**

  * **Linux \& Windows:**

    Copied

    &#x20;   ```
        reachy-mini-daemon --sim
        ```

  \* \*\*macOS:\*\*

  * **macOS:**

    Copied

    &#x20;   ```
        python -m reachy\\\_mini.daemon.app.main --sim
        ```



    ## \*\*5. Connecting your Code\*\*

    Once the simulation is running, it behaves exactly like a real \*\*Reachy Mini Lite\*\* connected via USB. The daemon listens on `localhost`, and you can run any Python SDK script without modification:

    ```

    from reachy\_mini import ReachyMini
from reachy\_mini.utils import create\_head\_pose

    # Connects to the simulation running on localhost

    with ReachyMini() as mini:
print("Connected to simulation!")

    &#x20;   # Look up and tilt head
    print("Moving head...")
    mini.goto\\\_target(
        head=create\\\_head\\\_pose(z=20, roll=10, mm=True, degrees=True),
        duration=1.0
    )

    # Wiggle antennas
    print("Wiggling antennas...")
    mini.goto\\\_target(antennas=\\\[0.6, -0.6], duration=0.3)
    mini.goto\\\_target(antennas=\\\[-0.6, 0.6], duration=0.3)

    # Reset to rest position
    mini.goto\\\_target(
        head=create\\\_head\\\_pose(),
        antennas=\\\[0, 0],
        duration=1.0
    )

    ```

## 

![리치_미니_소프트웨어_스택_다이어그램.png](리치_미니_소프트웨어_스택_다이어그램.png)



