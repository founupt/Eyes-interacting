import cv2
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

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
                left_pupil_x = int(face_landmarks.landmark[468].x * frame.shape[1])  
                left_pupil_y = int(face_landmarks.landmark[468].y * frame.shape[0])
                right_pupil_x = int(face_landmarks.landmark[473].x * frame.shape[1])  
                right_pupil_y = int(face_landmarks.landmark[473].y * frame.shape[0])

                cv2.circle(frame, (left_pupil_x, left_pupil_y), 5, (0, 255, 0), -1)  # xanh lá - mắt trái
                cv2.circle(frame, (right_pupil_x, right_pupil_y), 5, (255, 0, 0), -1)  # Màu xanh dương - mắt phải

                # Tính toán 4 điểm xung quanh con ngươi
                offset = 8  # Khoảng cách từ con ngươi đến các điểm px
                points_left = [
                    (left_pupil_x - offset, left_pupil_y),        
                    (left_pupil_x + offset, left_pupil_y),        
                    (left_pupil_x, left_pupil_y - offset),         
                    (left_pupil_x, left_pupil_y + offset)          
                ]
                
                points_right = [
                    (right_pupil_x - offset, right_pupil_y),       
                    (right_pupil_x + offset, right_pupil_y),       
                    (right_pupil_x, right_pupil_y - offset),      
                    (right_pupil_x, right_pupil_y + offset)       
                ]

                for point in points_left:
                    cv2.circle(frame, point, 3, (0, 255, 0), -1)  # Màu xanh lá

                for point in points_right:
                    cv2.circle(frame, point, 3, (255, 0, 0), -1)  # Màu xanh dương

                cv2.putText(frame, f'Left Pupil: ({left_pupil_x}, {left_pupil_y})', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                cv2.putText(frame, f'Right Pupil: ({right_pupil_x}, {right_pupil_y})', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 1)

        cv2.imshow("Eye Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

webcam.release()
cv2.destroyAllWindows()