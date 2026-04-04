"""학습 목표: 얼굴을 감지해 리치미니 헤드가 자동으로 따라보기"""

import cv2

from reachy_mini import ReachyMini

CAMERA_INDEX = 1  # 0: 내장 웹캠, 1: 외장 웹캠

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

with ReachyMini() as mini:
    mini.media.camera.cap.release()
    mini.media.camera.cap = cv2.VideoCapture(CAMERA_INDEX)
    # camera.resolution은 원래 카메라 기준이므로 외장 웹캠 실제 크기로 업데이트
    cam_w = int(mini.media.camera.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cam_h = int(mini.media.camera.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    mini.enable_motors()
    print("얼굴을 카메라 앞에 놓으면 헤드가 따라봅니다. 'q'로 종료.")

    while True:
        frame = mini.media.get_frame()
        if frame is None:
            continue

        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60),
        )

        if len(faces) > 0:
            # 가장 큰 얼굴 기준으로 추적
            x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])
            u, v = x + fw // 2, y + fh // 2

            # 외장 웹캠 해상도 → camera.resolution 범위로 보간
            res_w, res_h = mini.media.camera.resolution
            u = int(u * res_w / cam_w)
            v = int(v * res_h / cam_h)

            # 경계 clamp (assert: 0 < u < res_w)
            u = max(1, min(u, res_w - 2))
            v = max(1, min(v, res_h - 2))

            mini.look_at_image(u=u, v=v, duration=0)

            cv2.rectangle(frame, (x, y), (x + fw, y + fh), (0, 255, 0), 2)
            cv2.circle(frame, (u, v), 6, (0, 0, 255), -1)
            cv2.putText(frame, f"target: ({u}, {v})", (x, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No face", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (128, 128, 128), 2)

        cv2.circle(frame, (w // 2, h // 2), 5, (255, 255, 0), -1)
        cv2.imshow("Face Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()
    mini.goto_target(head=None, duration=1.0)
    mini.disable_motors()
