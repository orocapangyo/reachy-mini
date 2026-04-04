# Week 06: 동작 녹화 및 재생

## 학습 목표

- 로봇 동작 녹화 및 저장
- 녹화된 동작 재생
- Hugging Face Hub 활용

## 1. 개요

이번 주차에서는 Reachy Mini 로봇의 동작을 녹화하고 재생하는 방법을 학습합니다. 또한 Hugging Face Hub를 활용하여 녹화된 동작 데이터를 공유하고 관리하는 방법을 다룹니다.

## 2. 동작 녹화 (Motion Recording)

### 2.1 기본 녹화 개념

동작 녹화는 로봇의 관절 상태(위치, 속도, 토크 등)를 시간에 따라 기록하는 과정입니다.

```python
from reachy_mini import ReachyMini
import numpy as np
import json
import time

class MotionRecorder:
    def __init__(self, reachy: ReachyMini):
        self.reachy = reachy
        self.recorded_frames = []
        self.recording = False
        
    def start_recording(self, fps: int = 30):
        """녹화 시작"""
        self.recorded_frames = []
        self.recording = True
        self.fps = fps
        print(f"녹화 시작 (FPS: {fps})")
        
    def stop_recording(self):
        """녹화 중지"""
        self.recording = False
        print(f"녹화 완료: {len(self.recorded_frames)} 프레임")
        return self.recorded_frames
        
    def record_frame(self):
        """현재 관절 상태를 녹화"""
        if not self.recording:
            return
            
        frame = {
            'timestamp': time.time(),
            'joints': self.reachy.get_joint_positions(),
            'velocities': self.reachy.get_joint_velocities()
        }
        self.recorded_frames.append(frame)
        
    def save_to_file(self, filepath: str):
        """녹화된 동작을 파일로 저장"""
        data = {
            'fps': self.fps,
            'total_frames': len(self.recorded_frames),
            'frames': self.recorded_frames
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"저장 완료: {filepath}")
```

### 2.2 녹화 실행 예제

```python
from reachy_mini import ReachyMini
import time

# 로봇 연결
reachy = ReachyMini()
recorder = MotionRecorder(reachy)

# 5초 동안 녹화
recorder.start_recording(fps=30)

start_time = time.time()
while time.time() - start_time < 5.0:
    recorder.record_frame()
    time.sleep(1.0 / 30)  # 30 FPS

frames = recorder.stop_recording()
recorder.save_to_file("my_motion.json")
```

### 2.3 LeRobot 형식으로 녹화

Hugging Face의 LeRobot 형식을 사용하면 다양한 로봇 학습 프레임워크와 호환됩니다.

```python
from lerobot.common.datasets.lerobot_dataset import LeRobotDataset
import torch

class LeRobotRecorder:
    def __init__(self, dataset_name: str, robot_type: str = "reachy_mini"):
        self.dataset_name = dataset_name
        self.robot_type = robot_type
        self.episodes = []
        self.current_episode = []
        
    def start_episode(self):
        """에피소드 녹화 시작"""
        self.current_episode = []
        
    def record_step(self, observation: dict, action: dict):
        """한 스텝 녹화"""
        step = {
            'observation.state': torch.tensor(observation['state']),
            'action': torch.tensor(action['joints']),
        }
        self.current_episode.append(step)
        
    def end_episode(self):
        """에피소드 종료 및 저장"""
        self.episodes.append(self.current_episode)
        self.current_episode = []
        
    def save_dataset(self):
        """데이터셋 저장"""
        # LeRobot 형식으로 저장
        pass
```

## 3. 동작 재생 (Motion Playback)

### 3.1 기본 재생 클래스

```python
class MotionPlayer:
    def __init__(self, reachy: ReachyMini):
        self.reachy = reachy
        
    def load_from_file(self, filepath: str) -> dict:
        """파일에서 동작 데이터 로드"""
        with open(filepath, 'r') as f:
            return json.load(f)
            
    def play(self, motion_data: dict, speed: float = 1.0):
        """동작 재생"""
        fps = motion_data['fps']
        frames = motion_data['frames']
        
        print(f"재생 시작: {len(frames)} 프레임, 속도 {speed}x")
        
        for i, frame in enumerate(frames):
            # 관절 위치 설정
            self.reachy.set_joint_positions(frame['joints'])
            
            # 다음 프레임까지 대기
            time.sleep(1.0 / (fps * speed))
            
        print("재생 완료")
        
    def play_loop(self, motion_data: dict, loops: int = 3):
        """동작 반복 재생"""
        for i in range(loops):
            print(f"루프 {i + 1}/{loops}")
            self.play(motion_data)
```

### 3.2 부드러운 재생을 위한 보간

```python
import numpy as np
from scipy.interpolate import interp1d

class SmoothMotionPlayer(MotionPlayer):
    def interpolate_motion(self, motion_data: dict, target_fps: int = 60):
        """동작 데이터를 높은 FPS로 보간"""
        frames = motion_data['frames']
        original_fps = motion_data['fps']
        
        # 시간 배열 생성
        original_times = np.arange(len(frames)) / original_fps
        target_times = np.arange(0, original_times[-1], 1.0 / target_fps)
        
        # 관절별 보간
        joints_array = np.array([f['joints'] for f in frames])
        interpolated_joints = []
        
        for joint_idx in range(joints_array.shape[1]):
            joint_values = joints_array[:, joint_idx]
            interpolator = interp1d(original_times, joint_values, kind='cubic')
            interpolated_joints.append(interpolator(target_times))
            
        interpolated_joints = np.array(interpolated_joints).T
        
        # 새로운 동작 데이터 생성
        new_frames = [{'joints': joints.tolist()} for joints in interpolated_joints]
        
        return {
            'fps': target_fps,
            'total_frames': len(new_frames),
            'frames': new_frames
        }
```

## 4. Hugging Face Hub 활용

### Hugging Face란?

**Hugging Face**는 AI/ML 커뮤니티를 위한 플랫폼으로, 모델, 데이터셋, 애플리케이션을 공유하고 협업할 수 있는 생태계를 제공합니다.

#### 핵심 구성요소

| 구성요소 | 설명 | 예시 |
|---------|------|------|
| **Models** | 사전 학습된 AI 모델 저장소 | GPT, BERT, Stable Diffusion |
| **Datasets** | 학습/평가용 데이터셋 | 이미지, 텍스트, 로봇 동작 데이터 |
| **Spaces** | ML 앱 호스팅 서비스 | Gradio, Streamlit 데모 앱 |
| **Hub** | Git 기반 버전 관리 시스템 | 모델/데이터셋 버전 관리 |

#### 로봇 공학에서의 활용

Hugging Face는 최근 **로봇 학습(Robot Learning)** 분야에서도 핵심 플랫폼으로 자리잡고 있습니다:

1. **LeRobot 프로젝트**: Hugging Face에서 개발한 오픈소스 로봇 학습 프레임워크
2. **동작 데이터셋 공유**: 로봇 동작 데이터를 표준화된 형식으로 공유
3. **모델 배포**: 학습된 정책(Policy) 모델을 쉽게 배포하고 재사용
4. **커뮤니티 협업**: 전 세계 연구자들과 데이터/모델 공유

```
┌─────────────────────────────────────────────────────────────┐
│                    Hugging Face Hub                          │
├─────────────────┬─────────────────┬─────────────────────────┤
│     Models      │    Datasets     │        Spaces           │
│  ┌───────────┐  │  ┌───────────┐  │  ┌─────────────────┐    │
│  │ LeRobot   │  │  │ reachy-   │  │  │ Demo Apps       │    │
│  │ Policies  │  │  │ mini-     │  │  │ (Gradio)        │    │
│  │           │  │  │ emotions  │  │  │                 │    │
│  └───────────┘  │  └───────────┘  │  └─────────────────┘    │
└─────────────────┴─────────────────┴─────────────────────────┘
```

#### Reachy Mini와 Hugging Face

Pollen Robotics는 Hugging Face Hub를 통해 Reachy Mini의 동작 데이터를 공유합니다:

- **pollen-robotics/reachy-mini-emotions**: 감정 표현 동작 데이터셋
- 녹화된 동작을 JSON 형식으로 저장하고 Hub에 업로드
- `snapshot_download()`를 통해 자동 다운로드 및 캐싱

### LeRobot 프로젝트

**LeRobot**은 Hugging Face에서 개발한 오픈소스 로봇 학습 프레임워크로, 실제 로봇을 위한 AI 모델을 쉽게 학습하고 배포할 수 있게 해줍니다.

#### LeRobot이란?

```
┌────────────────────────────────────────────────────────────────┐
│                        LeRobot                                  │
│     "Making AI for Robotics more accessible"                   │
├────────────────────────────────────────────────────────────────┤
│  🎯 목표: 누구나 쉽게 로봇 AI를 학습하고 공유할 수 있는 환경    │
│  📦 구성: 데이터셋 + 정책(Policy) + 시뮬레이션 + 실제 로봇     │
│  🔗 통합: Hugging Face Hub와 완벽 연동                          │
└────────────────────────────────────────────────────────────────┘
```

#### 핵심 특징

| 특징 | 설명 |
|-----|------|
| **표준화된 데이터 형식** | 로봇 동작 데이터를 일관된 형식으로 저장/공유 |
| **다양한 정책 지원** | ACT, Diffusion Policy, TDMPC 등 최신 알고리즘 |
| **시뮬레이션 통합** | MuJoCo, PyBullet 등과 연동 |
| **실제 로봇 지원** | Koch, Aloha, SO-100, Reachy 등 |
| **Imitation Learning** | 시연 기반 학습으로 빠른 정책 학습 |

#### LeRobot 아키텍처

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Record    │───▶│   Train     │───▶│   Deploy    │
│   동작녹화   │    │   정책학습   │    │   로봇배포   │
└─────────────┘    └─────────────┘    └─────────────┘
       │                 │                   │
       ▼                 ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Dataset    │    │   Policy    │    │   Robot     │
│  (HF Hub)   │    │   (Model)   │    │  Hardware   │
└─────────────┘    └─────────────┘    └─────────────┘
```

#### 지원하는 로봇 플랫폼

| 로봇 | 유형 | 특징 |
|-----|------|------|
| **Koch v1.1** | 저가형 로봇팔 | 오픈소스, DIY 가능 |
| **Aloha** | 듀얼암 로봇 | 양손 조작, 텔레오퍼레이션 |
| **SO-100** | 데스크탑 암 | 컴팩트, 교육용 |
| **Reachy** | 휴머노이드 | 상체 로봇, Pollen Robotics |

#### 지원하는 정책 (Policy)

```python
# LeRobot에서 지원하는 주요 정책들
policies = {
    "ACT": "Action Chunking Transformer - 빠른 추론",
    "Diffusion Policy": "확산 모델 기반 - 복잡한 동작",
    "TDMPC": "Model Predictive Control - 계획 기반",
    "VQ-BeT": "Vector Quantized - 이산 행동 공간",
}
```

#### 설치 및 기본 사용

```bash
# LeRobot 설치
pip install lerobot

# 또는 개발 버전
git clone https://github.com/huggingface/lerobot.git
cd lerobot
pip install -e .
```

#### 데이터셋 구조 예시

LeRobot 데이터셋은 다음과 같은 구조로 저장됩니다:

```
dataset/
├── meta/
│   ├── info.json           # 데이터셋 메타정보
│   ├── episodes.jsonl      # 에피소드 정보
│   └── stats.json          # 통계 정보
├── data/
│   ├── chunk-000/
│   │   ├── episode_000000.parquet
│   │   └── episode_000001.parquet
│   └── ...
└── videos/                  # (선택) 비디오 데이터
    └── observation.images.top/
        ├── episode_000000.mp4
        └── ...
```

#### Reachy Mini와 LeRobot 연동

```python
from lerobot.common.datasets.lerobot_dataset import LeRobotDataset

# Reachy Mini 데이터셋 로드
dataset = LeRobotDataset("pollen-robotics/reachy-mini-example")

# 데이터 확인
for sample in dataset:
    observation = sample["observation.state"]  # 관절 상태
    action = sample["action"]                  # 실행할 동작
    # 정책 학습 또는 재생에 사용
```

### 4.1 Hugging Face Hub 설정

```bash
# Hugging Face CLI 설치
uv pip install huggingface_hub

# 로그인
huggingface-cli login
```

### 4.2 데이터셋 업로드

```python
from huggingface_hub import HfApi, Repository
import os

class HuggingFaceUploader:
    def __init__(self, username: str):
        self.api = HfApi()
        self.username = username
        
    def upload_motion_dataset(self, local_path: str, repo_name: str):
        """동작 데이터셋을 Hugging Face Hub에 업로드"""
        repo_id = f"{self.username}/{repo_name}"
        
        # 리포지토리 생성
        self.api.create_repo(repo_id, repo_type="dataset", exist_ok=True)
        
        # 파일 업로드
        self.api.upload_folder(
            folder_path=local_path,
            repo_id=repo_id,
            repo_type="dataset"
        )
        
        print(f"업로드 완료: https://huggingface.co/datasets/{repo_id}")
        
    def upload_single_file(self, filepath: str, repo_name: str):
        """단일 파일 업로드"""
        repo_id = f"{self.username}/{repo_name}"
        
        self.api.upload_file(
            path_or_fileobj=filepath,
            path_in_repo=os.path.basename(filepath),
            repo_id=repo_id,
            repo_type="dataset"
        )
```

### 4.3 데이터셋 다운로드

```python
from huggingface_hub import hf_hub_download, snapshot_download

def download_motion(repo_id: str, filename: str = None):
    """Hugging Face Hub에서 동작 데이터 다운로드"""
    if filename:
        # 단일 파일 다운로드
        path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            repo_type="dataset"
        )
    else:
        # 전체 데이터셋 다운로드
        path = snapshot_download(
            repo_id=repo_id,
            repo_type="dataset"
        )
    return path

# 사용 예시
motion_path = download_motion(
    "orocapangyo/reachy-mini-motions",
    "wave_hand.json"
)
```

### 4.4 LeRobot 데이터셋 활용

```python
from lerobot.common.datasets.lerobot_dataset import LeRobotDataset

# Hugging Face Hub에서 LeRobot 데이터셋 로드
dataset = LeRobotDataset(
    "orocapangyo/reachy_mini_wave",
    split="train"
)

# 데이터셋 정보 확인
print(f"총 에피소드 수: {dataset.num_episodes}")
print(f"총 프레임 수: {len(dataset)}")

# 첫 번째 프레임 확인
sample = dataset[0]
print(f"관절 상태: {sample['observation.state']}")
print(f"액션: {sample['action']}")
```

## 5. 실습 예제

### 5.1 전체 워크플로우 예제

```python
from reachy_mini import ReachyMini
import time

def main():
    # 1. 로봇 연결
    reachy = ReachyMini()
    
    # 2. 녹화
    recorder = MotionRecorder(reachy)
    recorder.start_recording(fps=30)
    
    print("손을 로봇에 올리고 동작을 가르쳐주세요...")
    print("5초 후 녹화가 시작됩니다.")
    time.sleep(5)
    
    print("녹화 중... (10초)")
    start_time = time.time()
    while time.time() - start_time < 10.0:
        recorder.record_frame()
        time.sleep(1.0 / 30)
    
    recorder.stop_recording()
    recorder.save_to_file("demo_motion.json")
    
    # 3. 재생
    player = MotionPlayer(reachy)
    motion_data = player.load_from_file("demo_motion.json")
    
    print("녹화된 동작을 재생합니다...")
    player.play(motion_data)
    
    # 4. Hub에 업로드 (선택사항)
    uploader = HuggingFaceUploader("your_username")
    uploader.upload_single_file("demo_motion.json", "reachy-mini-demos")

if __name__ == "__main__":
    main()
```

### 5.2 시뮬레이션에서 테스트

```bash
# 시뮬레이션 시작
reachy-mini-daemon --sim

# 다른 터미널에서 녹화/재생 스크립트 실행
python motion_demo.py
```

## 6. 추가 리소스

### 공식 문서
- [LeRobot GitHub](https://github.com/huggingface/lerobot)
- [Hugging Face Hub 문서](https://huggingface.co/docs/hub/)
- [Reachy Mini Developer Center](https://reachymini.net/developers.html)

### 관련 데이터셋
- [LeRobot Datasets](https://huggingface.co/collections/lerobot/lerobot-datasets-659fa4c31f8e7b35acbeb8be)
- [orocapangyo/reachy-mini-motions](https://huggingface.co/datasets/orocapangyo/reachy-mini-motions)

---

**작성일**: 2025-01-16
**참고 리포지토리**: https://github.com/orocapangyo/reachy_mini
**라이선스**: Apache 2.0
