# Recorded Motion Guide

`recorded_motion.py`는 Reachy Mini 동작을 녹화/저장/재생하는 통합 CLI 도구입니다.

## 사전 준비

1. Reachy Mini Control App(시뮬레이터) 실행
2. 프로젝트 폴더 이동 및 가상환경 활성화

```bash
cd /Users/baejiu/study/reachy_mini
source .venv/bin/activate
```

## 기본 명령

### 1) 자동 데모 녹화 + 즉시 재생

```bash
python recorded_motion.py demo
```

### 2) 수동 녹화(5초) 후 파일 저장

```bash
python recorded_motion.py record --manual --duration 5 -o recordings/my_motion.json
```

### 3) 저장한 파일 재생

```bash
python recorded_motion.py play -i recordings/my_motion.json
```

### 4) Hugging Face 동작 라이브러리 재생

```bash
python recorded_motion.py hf-play -l dance
python recorded_motion.py hf-play -l emotions
python recorded_motion.py hf-play -l dance -m chicken_peck
```

## Dance 라이브러리 동작 이름 예시

- `stumble_and_recover`
- `chin_lead`
- `head_tilt_roll`
- `jackson_square`
- `pendulum_swing`
- `side_glance_flick`
- `grid_snap`
- `simple_nod`
- `side_to_side_sway`
- `polyrhythm_combo`
- `interwoven_spirals`
- `uh_huh_tilt`
- `chicken_peck`
- `yeah_nod`
- `side_peekaboo`
- `dizzy_spin`
- `neck_recoil`
- `groovy_sway_and_roll`
- `sharp_side_tilt`

## Docs API에서 바로 재생하기

`http://127.0.0.1:8000/docs`에서 아래 순서로 실행합니다.

1. `GET /api/move/recorded-move-datasets/list/{dataset_name}`
2. `dataset_name`에 `pollen-robotics/reachy-mini-dances-library` 입력 후 `Execute`
3. 목록에서 `move_name` 확인 (예: `chicken_peck`)
4. `POST /api/move/play/recorded-move-dataset/{dataset_name}/{move_name}` 실행

예시:

- `dataset_name`: `pollen-robotics/reachy-mini-dances-library`
- `move_name`: `chicken_peck`
