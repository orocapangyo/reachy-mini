<<<<<<< HEAD
# reachy-mini

## 소개

reachy-mini는 소형 로봇 플랫폼 또는 소프트웨어 프로젝트로, 간단한 제어, 시뮬레이션, 또는 로봇 동작 테스트를 위해 설계되었습니다. 이 프로젝트는 사용자가 손쉽게 로봇의 동작을 제어하고, 다양한 실험을 수행할 수 있도록 직관적인 인터페이스와 확장 가능한 구조를 제공합니다.

## 주요 특징

- 간단한 설치 및 실행
- 모듈화된 구조로 손쉬운 확장성
- 다양한 로봇 동작 예제 제공
- 시뮬레이션 및 실제 하드웨어 연동 지원(필요시)

## 서브모듈

이 프로젝트는 Git Submodule을 사용하여 외부 저장소를 포함하고 있습니다.

### reachy_mini

- **경로**: `reachy_mini/`
- **브랜치**: `develop`
- **저장소**: https://github.com/orocapangyo/reachy_mini.git
- **목적**: Reachy Mini 로봇의 공식 Python SDK 및 시뮬레이션 프레임워크 (개발 버전)

### reachy_mini_stl_convexify

- **경로**: `reachy_mini_stl_convexify/`
- **브랜치**: `main`
- **저장소**: https://github.com/orocapangyo/reachy_mini_stl_convexify.git
- **목적**: Reachy Mini 로봇의 STL 파일을 convex hull로 변환하여 물리 시뮬레이션 성능 최적화

### 서브모듈 사용 방법

```bash
# 처음 클론할 때
git clone --recurse-submodules https://github.com/orocapangyo/reachy-mini.git

# 이미 클론한 경우 서브모듈 초기화
git submodule update --init --recursive

# 서브모듈 업데이트
git submodule update --remote
```

## 관련 영상

[![reachy-mini 소개 영상](https://img.youtube.com/vi/JvdBJZ-qR18/0.jpg)](https://youtu.be/JvdBJZ-qR18?si=qhe4JHv3QVOF-5la)

해당 영상을 클릭하면 YouTube에서 자세한 내용을 확인할 수 있습니다.

## 기여자 (Contributors)

| No. | 이름 | 이메일 | GitHub |
|-----|------|--------|---------|
| 1 | 하범수 | habemsu7@gmail.com | BeomsuHa |
| 2 | 최정호 | ho8909585y@gmail.com   |  |
| 3 | 이하빈 | ihb0126@gmail.com | yabeeu0126 |
| 4 | 나승원 | jws10375@gmail.com | lala4768 |
| 5 | 이세현 | a93450311@gmail.com | - |
| 6 | 임태양 | jennetime98@gmail.com | jenlime98 |
| 7 | 이주선 | km01049@gmail.com | km01049 |
| 8 | 서다원 | tjekdnjs96@gmail.com | seodawon |
| 9 | 정재욱 | m6488kk@gmail.com | - |
| 10 | 문진환 | jhmoon0224@gmail.com  | - |
=======
# Reachy Mini 🤖

[![Ask on HuggingChat](https://img.shields.io/badge/Ask_on-HuggingChat-yellow?logo=huggingface&logoColor=yellow&style=for-the-badge)](https://huggingface.co/chat/?attachments=https%3A%2F%2Fgist.githubusercontent.com%2FFabienDanieau%2F919e1d7468fb16e70dbe984bdc277bba%2Fraw%2Fdoc_reachy_mini_full.md&prompt=Read%20this%20documentation%20about%20Reachy%20Mini%20so%20I%20can%20ask%20questions%20about%20it.)
[![Discord](https://img.shields.io/badge/Discord-Join_the_Community-7289DA?logo=discord&logoColor=white)](https://discord.gg/Y7FgMqHsub)

**Reachy Mini is an open-source, expressive robot made for hackers and AI builders.**

🛒 [**Buy Reachy Mini**](https://www.hf.co/reachy-mini/)

[![Reachy Mini Hello](/docs/assets/reachy_mini_hello.gif)](https://www.pollen-robotics.com/reachy-mini/)

## ⚡️ Build and start your own robot

**Choose your platform to access the specific guide:**

| **🤖 Reachy Mini (Wireless)** | **🔌 Reachy Mini Lite** | **💻 Simulation** |
| :---: | :---: | :---: |
| The full autonomous experience.<br>Raspberry Pi 4 + Battery + WiFi. | The developer version.<br>USB connection to your computer. | No hardware required.<br>Prototype in MuJoCo. |
| 👉 [**Go to Wireless Guide**](docs/platforms/reachy_mini/get_started.md) | 👉 [**Go to Lite Guide**](docs/platforms/reachy_mini_lite/get_started.md) | 👉 [**Go to Simulation**](docs/platforms/simulation/get_started.md) |



> ⚡ **Pro tip:** Install [uv](https://docs.astral.sh/uv/getting-started/installation/) for 10-100x faster app installations (auto-detected, falls back to `pip`).

<br>

## 📱 Apps & Ecosystem

Reachy Mini comes with an app store powered by Hugging Face Spaces. You can install these apps directly from your robot's dashboard with one click!

* **🗣️ [Conversation App](https://huggingface.co/spaces/pollen-robotics/reachy_mini_conversation_app):** Talk naturally with Reachy Mini (powered by LLMs).
* **📻 [Radio](https://huggingface.co/spaces/pollen-robotics/reachy_mini_radio):** Listen to the radio with Reachy Mini !
* **👋 [Hand Tracker](https://huggingface.co/spaces/pollen-robotics/hand_tracker_v2):** The robot follows your hand movements in real-time.

👉 [**Browse all apps on Hugging Face**](https://hf.co/reachy-mini/#/apps)

<br>

## 🚀 Getting Started with Reachy Mini SDK

### Quick Look
Control your robot in just **a few lines of code**:

```python
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

with ReachyMini() as mini:
    # Look up and tilt head
    mini.goto_target(
        head=create_head_pose(z=10, roll=15, degrees=True, mm=True),
        duration=1.0
    )
```

### User guides
* **[Installation](docs/SDK/installation.md)**: 5 minutes to set up your computer
* **[Quickstart Guide](docs/SDK/quickstart.md)**: Run your first behavior on Reachy Mini
* **[Python SDK](docs/SDK/python-sdk.md)**: Learn to move, see, speak, and hear.
* **[AI Integrations](docs/SDK/integration.md)**: Connect LLMs, build Apps, and publish to Hugging Face.
* **[Core Concepts](docs/SDK/core-concept.md)**: Architecture, coordinate systems, and safety limits.
* 🤗[**Share your app with the community**](https://huggingface.co/blog/pollen-robotics/make-and-publish-your-reachy-mini-apps)
* 📂 [**Browse the Examples Folder**](examples)


<br>

## 🛠 Hardware Overview

Reachy Mini robots are sold as kits and generally take **2 to 3 hours** to assemble. Detailed step-by-step guides are available in the platform-specific folders linked above.

* **Reachy Mini (Wireless):** Runs onboard (RPi 4), autonomous, includes IMU. [See specs](docs/platforms/reachy_mini/hardware.md).
* **Reachy Mini Lite:** Runs on your PC, powered via wall outlet. [See specs](docs/platforms/reachy_mini_lite/hardware.md).

<br>

## ❓ Troubleshooting

Encountering an issue? 👉 **[Check the Troubleshooting & FAQ Guide](/docs/troubleshooting.md)**

<br>

## 🤝 Community & Contributing

* **Join the Community:** Join [Discord](https://discord.gg/2bAhWfXme9) to share your moments with Reachy, build apps together, and get help.
* **Found a bug?** Open an issue on this repository.


## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.
Hardware design files are licensed under Creative Commons BY-SA-NC.
>>>>>>> upstream/main
