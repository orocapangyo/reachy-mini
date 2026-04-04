"""학습 목표: OpenCV Haar Cascade로 얼굴 감지 + 화면에 표시"""

import cv2

from reachy_mini import ReachyMini

CAMERA_INDEX = 1  # 0: 내장 웹캠, 1: 외장 웹캠

# OpenCV 내장 얼굴 감지 모델 (별도 설치 불필요)
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

with ReachyMini() as mini:
    # 외장 웹캠으로 교체
    mini.media.camera.cap.release()
    mini.media.camera.cap = cv2.VideoCapture(CAMERA_INDEX)

    print("카메라 앞에 얼굴을 놓아보세요. 'q'로 종료.")

    while True:
        frame = mini.media.get_frame()
        if frame is None:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 얼굴 감지
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60),
        )

        for x, y, w, h in faces:
            cx, cy = x + w // 2, y + h // 2
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            cv2.putText(frame, f"face ({cx}, {cy})", (x, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.putText(frame, f"Faces: {len(faces)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)

        cv2.imshow("Face Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()
