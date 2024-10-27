import cv2
import mediapipe as mp
import pyautogui

# Khởi tạo camera và Mediapipe Face Mesh
cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()

while True:
    # Đọc khung hình từ camera
    _, frame = cam.read()
    frame = cv2.flip(frame, 1)  # Lật khung hình
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Chuyển đổi sang RGB
    output = face_mesh.process(rgb_frame)  # Xử lý khung hình với Face Mesh

    # Lấy các điểm landmark
    landmark_points = output.multi_face_landmarks
    frame_h, frame_w, _ = frame.shape

    if landmark_points:
        landmarks = landmark_points[0].landmark

        # Vẽ các điểm landmark cho toàn bộ khuôn mặt
        for landmark in landmarks:
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)
            cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)  # Vẽ điểm màu xanh

        # Điều khiển chuột theo một điểm landmark cụ thể (ví dụ: mũi)
        nose_index = 1  # Thay đổi chỉ số nếu cần
        nose_landmark = landmarks[nose_index]
        screen_x = screen_w * nose_landmark.x
        screen_y = screen_h * nose_landmark.y
        pyautogui.moveTo(screen_x, screen_y)

    # Hiển thị khung hình
    cv2.imshow('Face Mesh Tracking', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Nhấn 'q' để thoát
        break

# Giải phóng camera và đóng cửa sổ
cam.release()
cv2.destroyAllWindows()