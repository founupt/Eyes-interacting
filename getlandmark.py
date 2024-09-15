import cv2
import mediapipe as mp

# Thiết lập Mediapipe
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# Mở webcam
webcam = cv2.VideoCapture(0)

print("Nhấn 'q' để dừng chương trình.")

with mp_face_mesh.FaceMesh(refine_landmarks=True) as face_mesh:
    while True:
        ret, frame = webcam.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = face_mesh.process(rgb_frame)

        if output.multi_face_landmarks:
            for face_landmarks in output.multi_face_landmarks:
                # Lấy tọa độ tròng đen
                left_pupil_x = int(face_landmarks.landmark[468].x * frame.shape[1])  # Tròng đen bên trái
                left_pupil_y = int(face_landmarks.landmark[468].y * frame.shape[0])
                right_pupil_x = int(face_landmarks.landmark[473].x * frame.shape[1])  # Tròng đen bên phải
                right_pupil_y = int(face_landmarks.landmark[473].y * frame.shape[0])

                # Vẽ tròng đen
                cv2.circle(frame, (left_pupil_x, left_pupil_y), 5, (0, 255, 0), -1)  # Màu xanh lá cho mắt trái
                cv2.circle(frame, (right_pupil_x, right_pupil_y), 5, (255, 0, 0), -1)  # Màu xanh dương cho mắt phải

                # Tính toán 4 điểm xung quanh con ngươi
                offset = 8  # Khoảng cách từ con ngươi đến các điểm
                points_left = [
                    (left_pupil_x - offset, left_pupil_y),         # Trái
                    (left_pupil_x + offset, left_pupil_y),         # Phải
                    (left_pupil_x, left_pupil_y - offset),         # Trên
                    (left_pupil_x, left_pupil_y + offset)          # Dưới
                ]
                
                points_right = [
                    (right_pupil_x - offset, right_pupil_y),       # Trái
                    (right_pupil_x + offset, right_pupil_y),       # Phải
                    (right_pupil_x, right_pupil_y - offset),       # Trên
                    (right_pupil_x, right_pupil_y + offset)        # Dưới
                ]

                # Vẽ 4 điểm xung quanh con ngươi
                for point in points_left:
                    cv2.circle(frame, point, 3, (0, 255, 0), -1)  # Màu xanh lá

                for point in points_right:
                    cv2.circle(frame, point, 3, (255, 0, 0), -1)  # Màu xanh dương

                # Hiển thị tọa độ
                cv2.putText(frame, f'Left Pupil: ({left_pupil_x}, {left_pupil_y})', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                cv2.putText(frame, f'Right Pupil: ({right_pupil_x}, {right_pupil_y})', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 1)

        cv2.imshow("Eye Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

webcam.release()
cv2.destroyAllWindows()