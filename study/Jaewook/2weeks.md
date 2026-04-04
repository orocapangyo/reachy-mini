📌 2주차: 기본 동작 제어 (Reachy Mini)
1. 학습 목표
•	머리(Head)와 안테나(Antenna) 제어 방법 이해
•	goto_target vs set_target 차이 파악
•	안전한 동작 범위(Safety Limits) 이해

⚙️ 2. 실습 환경 준비
✔ 기본 구조
•	시뮬레이터: MuJoCo 기반
•	제어 방식: Python → daemon → 웹 대시보드

✔ 실행 흐름
1.	가상환경 활성화
2.	시뮬레이터 실행
3.	브라우저 확인
4.	Python 코드 실행
reachy-mini-daemon --sim
→ http://localhost:8000
👉 핵심:
•	데몬은 계속 켜둬야 함
•	코드는 별도 터미널에서 실행

🤖 3. 머리(Head) 제어
✔ 좌표계
•	x: 앞/뒤
•	y: 좌/우
•	z: 위/아래
✔ 기본 이동
pose = create_head_pose(y=-10, mm=True)
mini.goto_target(head=pose, duration=2.0)
👉 포인트:
•	mm=True → 단위 mm
•	duration → 움직임 속도 (부드러움 결정)

🔄 4. 회전 제어 (Rotation)
✔ 3가지 회전 축
•	Roll → 좌우 기울기
•	Pitch → 끄덕임
•	Yaw → 좌우 회전
✔ 예제
pose = create_head_pose(pitch=15, yaw=-25, degrees=True)
👉 핵심:
•	degrees=True → 각도 단위(degree)
•	기본은 radian

📡 5. 안테나 제어
✔ 구조
•	0번 → 왼쪽
•	1번 → 오른쪽
✔ 기본 제어
mini.goto_target(antennas=np.deg2rad([45, 45]))
👉 포인트:
•	반드시 radian 사용
•	np.deg2rad() 필수

🔀 6. 복합 동작
✔ 동시에 제어
mini.goto_target(
    head=pose,
    antennas=np.deg2rad([45,45]),
    body_yaw=np.deg2rad(30),
    duration=2.0
)
👉 핵심:
•	여러 부위 동시 제어 가능
✔ 순차 동작
mini.goto_target(...)
mini.goto_target(...)
mini.goto_target(...)
👉 핵심:
•	단계별 동작 구현 가능
•	로봇 "행동 시나리오" 구성 가능
________________________________________
⚡ 7. goto_target vs set_target
✔ goto_target
•	부드러운 이동 (보간)
•	완료까지 대기 (블로킹)
•	실제 로봇에 적합
mini.goto_target(..., duration=2.0)
________________________________________
✔ set_target
•	즉시 반응
•	논블로킹
•	실시간 제어에 적합
mini.set_target(...)
🛑 8. 안전 범위 (Safety Limits)
✔ 일반적인 범위
•	Head 이동: ±50mm
•	회전: ±45°
•	안테나: 0~90°
•	Body yaw: ±60°
________________________________________
✔ 좋은 예 vs 나쁜 예
✔ 좋은 예
y=-10 → y=-20 (점진적 이동)
❌ 나쁜 예
y=-50, duration=0.1 (급격한 이동)
________________________________________
✔ 에러 처리
try:
    mini.goto_target(...)
except:
    mini.goto_target(create_head_pose())
👉 항상 초기 위치 복귀 로직 필요
________________________________________
📈 9. 실제 예제 핵심 (GitHub)
✔ minimal_demo
•	사인파 기반 움직임
•	자연스러운 반복 동작
👉 핵심 공식:
sin(2πft)
•	f = 0.5Hz → 2초에 1번 반복
________________________________________
✔ sequence
•	yaw / pitch / roll 각각 분리 제어
•	rotation matrix 기반 제어
👉 특징:
•	더 정밀한 제어 가능
•	실시간 업데이트 (set_target)
________________________________________
🎯 10. 핵심 정리 (한 장 요약)
✔ Head → 위치 + 회전 제어
✔ Antenna → radian 기반 각도 제어
✔ goto_target → 부드러운 동작
✔ set_target → 빠른 실시간 제어
✔ Safety → 범위 + 속도 중요
________________________________________
🔥 발표용 한 줄 결론
👉 “Reachy Mini는 위치·회전·시간을 조합해서
자연스러운 로봇 동작을 만드는 구조다.”
