import cv2 
import mediapipe as mp
import pyautogui
import time

mp_face_mesh = mp.solutions.face_mesh

camera_w, camera_h = 1280, 720  # Tăng độ phân giải để cải thiện hình ảnh
screen_w, screen_h = pyautogui.size()

blink_count_left = 0
blink_count_right = 0
double_blink_duration = 0.4
start_time_blink_left = None
start_time_blink_right = None
last_x, last_y = screen_w // 2, screen_h // 2
movement_threshold = 10  # Ngưỡng để giảm độ giật của con trỏ chuột

def process_frame(frame):
    global blink_count_left, blink_count_right, start_time_blink_left, start_time_blink_right, last_x, last_y

    frame = cv2.flip(frame, 1)

    with mp_face_mesh.FaceMesh(refine_landmarks=True) as face_mesh:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = face_mesh.process(rgb_frame)

        if output.multi_face_landmarks:
            landmarks = output.multi_face_landmarks[0].landmark

            left_pupil_x = int(landmarks[468].x * screen_w)
            left_pupil_y = int(landmarks[468].y * screen_h)
            right_pupil_x = int(landmarks[473].x * screen_w)
            right_pupil_y = int(landmarks[473].y * screen_h)

            target_x = (left_pupil_x + right_pupil_x) // 2
            target_y = (left_pupil_y + right_pupil_y) // 2

            # Chỉ di chuyển con trỏ chuột nếu khoảng cách di chuyển đủ lớn, giúp giảm giật
            if abs(target_x - last_x) > movement_threshold or abs(target_y - last_y) > movement_threshold:
                pyautogui.moveTo(target_x, target_y)
                last_x, last_y = target_x, target_y

            left_eye_closed = (landmarks[145].y - landmarks[159].y) < 0.004
            right_eye_closed = (landmarks[374].y - landmarks[386].y) < 0.004

            # Nhấp chuột trái khi nháy mắt trái 2 lần
            if left_eye_closed:
                blink_count_left += 1
                if blink_count_left == 1:
                    start_time_blink_left = time.time()
                if blink_count_left >= 2 and (time.time() - start_time_blink_left < double_blink_duration):
                    pyautogui.click(button='left')  # Nhấp chuột trái
                    blink_count_left = 0
                elif blink_count_left == 1:
                    pass  # Single blink, có thể xử lý tại đây nếu cần
            else:
                blink_count_left = 0

            # Nhấp chuột phải khi nháy mắt phải 2 lần
            if right_eye_closed:
                blink_count_right += 1
                if blink_count_right == 1:
                    start_time_blink_right = time.time()
                if blink_count_right >= 2 and (time.time() - start_time_blink_right < double_blink_duration):
                    pyautogui.click(button='right')  # Nhấp chuột phải
                    blink_count_right = 0
                elif blink_count_right == 1:
                    pass
            else:
                blink_count_right = 0

            cv2.circle(frame, (target_x, target_y), 10, (0, 255, 0), -1)  # Hiển thị điểm nhắm chuột trên frame

    return frame

def get_camera_frame(cap):
    ret, frame = cap.read()
    if ret:
        return frame
    else:
        return None
