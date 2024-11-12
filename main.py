import cv2
import mediapipe as mp
import pyautogui
import time
from gaze_tracking import GazeTracking

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)

face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = 1920, 1080

last_x, last_y = screen_w // 2, screen_h // 2

def smooth_move(target_x, target_y, current_x, current_y, smoothing_factor=0.5):
    new_x = current_x + (target_x - current_x) * smoothing_factor
    new_y = current_y + (target_y - current_y) * smoothing_factor
    return int(new_x), int(new_y)

blink_count_left = 0
blink_count_right = 0
start_time_blink_left = None
start_time_blink_right = None
hold_start_time = None
hold_duration = 5  
program_paused = False

print("Nhấn 'q' để dừng chương trình.")

while True:
    _, frame = webcam.read()
    frame = cv2.flip(frame, 1)

    gaze.refresh(frame)
    annotated_frame = gaze.annotated_frame()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    landmark_points = output.multi_face_landmarks
    frame_h, frame_w, _ = frame.shape

    if landmark_points:
        landmarks = landmark_points[0].landmark

        left_eye = [landmarks[133], landmarks[144], landmarks[145], landmarks[153]]  
        right_eye = [landmarks[362], landmarks[382], landmarks[373], landmarks[380]]

        left_pupil_x = int(sum([landmark.x for landmark in left_eye]) / len(left_eye) * screen_w)
        left_pupil_y = int(sum([landmark.y for landmark in left_eye]) / len(left_eye) * screen_h)

        right_pupil_x = int(sum([landmark.x for landmark in right_eye]) / len(right_eye) * screen_w)
        right_pupil_y = int(sum([landmark.y for landmark in right_eye]) / len(right_eye) * screen_h)

        target_x = (left_pupil_x + right_pupil_x) // 2
        target_y = (left_pupil_y + right_pupil_y) // 2

        if target_y < screen_h * 0.1:  # Nếu gần phần trên cùng
            target_y = max(0, target_y - 20)  # Giảm tọa độ y để dễ di chuyển lên

        target_x = max(0, min(target_x, screen_w - 1))
        target_y = max(0, min(target_y, screen_h - 1))

        last_x, last_y = smooth_move(target_x, target_y, last_x, last_y, smoothing_factor=0.5)
        pyautogui.moveTo(last_x, last_y)

        left = [landmarks[145], landmarks[159]]
        if (left[0].y - left[1].y) < 0.004:
            blink_count_left += 1
            if blink_count_left == 1 and not program_paused:
                pyautogui.click()  
                print('Click chuột trái')
            if start_time_blink_left is None:
                start_time_blink_left = time.time()
        else:
            if start_time_blink_left is not None:
                if (time.time() - start_time_blink_left) < 1:  
                    if blink_count_left >= 2:
                        pyautogui.click()  
                        print('Double click chuột trái')
                blink_count_left = 0  
            start_time_blink_left = None

        right = [landmarks[474], landmarks[478]] if len(landmarks) > 478 else None
        if right and (right[0].y - right[1].y) < 0.004:
            blink_count_right += 1
            if blink_count_right == 1 and not program_paused:
                pyautogui.click(button='right')  
                print('Click chuột phải')
            if start_time_blink_right is None:
                start_time_blink_right = time.time()
        else:
            if start_time_blink_right is not None:
                if (time.time() - start_time_blink_right) < 1:  
                    if blink_count_right >= 2:
                        pyautogui.click(button='right')  
                        print('Double click chuột phải')
                blink_count_right = 0  
            start_time_blink_right = None

        # Kiểm tra nhắm cả hai mắt
        if gaze.is_blinking() and gaze.is_center() and not program_paused:
            if hold_start_time is None:
                hold_start_time = time.time()
        elif hold_start_time is not None:
            if (time.time() - hold_start_time) >= hold_duration:
                print("Chương trình đang tạm dừng")
                program_paused = True
                hold_start_time = None  
        else:
            if program_paused and not gaze.is_blinking():
                print("Chương trình hiện đang khởi chạy")
                program_paused = False

    else:
        print("Không phát hiện khuôn mặt.")

    # Hiển thị trạng thái
    text = ""
    if gaze.is_blinking():
        text = "Blinking"
    elif gaze.is_right():
        text = "Looking right"
    elif gaze.is_left():
        text = "Looking left"
    elif gaze.is_center():
        text = "Looking center"

    cv2.putText(annotated_frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

    # Hiển thị tọa độ x của con ngươi
    # cv2.putText(annotated_frame, f"L: {left_pupil_x:.1f} R: {right_pupil_x:.1f}", (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

    cv2.imshow("Eye Controlled Mouse", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Đang dừng chương trình...")
        break

webcam.release()
cv2.destroyAllWindows()