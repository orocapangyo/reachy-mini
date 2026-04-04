"""학습 목표 1: 카메라 영상 취득 및 OpenCV로 화면 표시"""

import cv2

from reachy_mini import ReachyMini

with ReachyMini() as mini:
    print("카메라 해상도:", mini.media.camera.resolution)
    print("'q' 키를 누르면 종료합니다.")

    while True:
        frame = mini.media.get_frame()

        if frame is None:
            continue

        cv2.imshow("Reachy Mini - Camera", frame)

        # 화면 중심점 표시
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2
        cv2.circle(frame, (cx, cy), 8, (0, 255, 0), -1)
        cv2.putText(frame, f"center: ({cx}, {cy})", (cx + 10, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.imshow("Reachy Mini - Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()
