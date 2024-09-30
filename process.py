import cv2
import mediapipe as mp
import pyautogui
import time

mp_face_mesh = mp.solutions.face_mesh
webcam = cv2.VideoCapture(0)

# Đặt độ phân giải để cải thiện hiệu suất
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

screen_w, screen_h = 1920, 1080
last_x, last_y = screen_w // 2, screen_h // 2

def smooth_move(target_x, target_y, current_x, current_y, smoothing_factor=1):
    new_x = current_x + (target_x - current_x) * smoothing_factor
    new_y = current_y + (target_y - current_y) * smoothing_factor
    return int(new_x), int(new_y)

blink_count_left = 0
blink_count_right = 0
double_blind_duration = 4  
double_blind_start_time = None

print("Nhấn 'q' để dừng chương trình.")

with mp_face_mesh.FaceMesh(refine_landmarks=True) as face_mesh:
    while True:
        ret, frame = webcam.read()
        if not ret or frame is None:
            print("Không thể lấy khung hình từ camera.")
            continue 

        # Lật khung hình để điều chỉnh hướng di chuyển chuột đúng
        frame = cv2.flip(frame, 1)
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
            
            target_x = max(0, min(target_x, screen_w - 1))
            target_y = max(0, min(target_y, screen_h - 1))

            last_x, last_y = smooth_move(target_x, target_y, last_x, last_y, smoothing_factor=0.5)
            pyautogui.moveTo(last_x, last_y)

            # Nhận diện nháy mắt
            left_eye_closed = (landmarks[145].y - landmarks[159].y) < 0.004
            right_eye_closed = (landmarks[374].y - landmarks[386].y) < 0.004  

            if left_eye_closed:
                blink_count_left += 1
                if blink_count_left == 1:
                    start_time_blink_left = time.time()
                if blink_count_left >= 2 and (time.time() - start_time_blink_left < 0.8):
                    pyautogui.click(button='left')  
                    print('Double click chuột trái')
                    blink_count_left = 0  
                elif blink_count_left == 1:
                    pyautogui.click(button='left') 
                    print('Click chuột trái')
            else:
                blink_count_left = 0  

            if right_eye_closed:
                blink_count_right += 1
                if blink_count_right == 1:
                    start_time_blink_right = time.time()
                if blink_count_right >= 2 and (time.time() - start_time_blink_right < 0.4):
                    pyautogui.click(button='right')  
                    print('Double click chuột phải')
                    blink_count_right = 0  
                elif blink_count_right == 1:
                    pyautogui.click(button='right') 
                    print('Click chuột phải')
            else:
                blink_count_right = 0  

            if left_eye_closed and right_eye_closed:
                if double_blind_start_time is None:
                    double_blind_start_time = time.time()
                elif time.time() - double_blind_start_time >= double_blind_duration:
                    print("Đang dừng chương trình do nhắm cả hai mắt.")
                    break  
            else:
                if double_blind_start_time is not None:
                    duration_closed = time.time() - double_blind_start_time
                    if duration_closed < 0.5:  
                        double_blind_start_time = None
                else:
                    double_blind_start_time = None  

            # Hiển thị trạng thái di chuyển mắt lên màn hình
            gaze_text = ""
            center_width = 200
            center_height = 200
            center_x_start = (screen_w - center_width) / 2
            center_x_end = center_x_start + center_width
            center_y_start = (screen_h - center_height) / 2
            center_y_end = center_y_start + center_height
            
            if left_pupil_y < screen_h / 2:
                if left_pupil_x < screen_w / 3:
                    gaze_text = "Moving Up Left"
                elif left_pupil_x < 2 * screen_w / 3:
                    gaze_text = "Moving Up Middle"
                else:
                    gaze_text = "Moving Up Right"
            else:
                if left_pupil_x < screen_w / 3:
                    gaze_text = "Moving Down Left"
                elif left_pupil_x < 2 * screen_w / 3:
                    gaze_text = "Moving Down Middle"
                else:
                    gaze_text = "Moving Down Right"
            if (left_pupil_x >= center_x_start and left_pupil_x <= center_x_end) and \
               (left_pupil_y >= center_y_start and left_pupil_y <= center_y_end):
                gaze_text = "Center"

            # Vẽ lên màn hình hướng di chuyển
            cv2.putText(frame, gaze_text, (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1.5, (147, 58, 31), 2)
            
            # Vẽ vị trí tracking mắt (dấu chấm ở vị trí mắt nhìn tới)
            cv2.circle(frame, (target_x, target_y), 10, (0, 255, 0), -1)

            cv2.imshow("Face Controlled Mouse", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Đang dừng chương trình...")
            break

webcam.release()
cv2.destroyAllWindows()
