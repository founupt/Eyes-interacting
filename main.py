import cv2
import mediapipe as mp
import pyautogui
import time
from gaze_tracking import GazeTracking

# Khởi tạo GazeTracking
gaze = GazeTracking()
webcam = cv2.VideoCapture(0)

# Khởi tạo Mediapipe Face Mesh
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()

# Biến để lưu vị trí con trỏ
last_x, last_y = screen_w // 2, screen_h // 2
smooth_factor = 0.1  # Hệ số làm mượt

blink_count_left = 0
blink_count_right = 0
start_time_blink_left = None
start_time_blink_right = None
hold_start_time = None
hold_duration = 5  # 5 giây
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
        num_landmarks = len(landmarks)

        # Tính toán vị trí con trỏ chuột
        if gaze.pupil_left_coords():
            pupil_x = int(screen_w * (gaze.pupil_left_coords()[0] / frame_w))
            pupil_y = int(screen_h * (gaze.pupil_left_coords()[1] / frame_h))
        else:
            pupil_x, pupil_y = last_x, last_y  # Giữ nguyên nếu không phát hiện đồng tử

        # Lọc chuyển động
        last_x += (pupil_x - last_x) * smooth_factor
        last_y += (pupil_y - last_y) * smooth_factor

        # Di chuyển con trỏ chuột
        pyautogui.moveTo(int(last_x), int(last_y))

        # Vẽ các điểm đồng tử
        for id, landmark in enumerate(landmarks[474:478]):
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)
            cv2.circle(frame, (x, y), 3, (0, 255, 0))

        # Kiểm tra nháy mắt trái
        left = [landmarks[145], landmarks[159]]
        if (left[0].y - left[1].y) < 0.004:
            blink_count_left += 1
            if blink_count_left == 1 and not program_paused:
                pyautogui.click()  # Click chuột trái
                print('Click chuột trái')
            if start_time_blink_left is None:
                start_time_blink_left = time.time()
        else:
            if start_time_blink_left is not None:
                if (time.time() - start_time_blink_left) < 1:  
                    if blink_count_left >= 2:
                        pyautogui.click()  # Double click chuột trái
                        print('Double click chuột trái')
                blink_count_left = 0  
            start_time_blink_left = None

        # Kiểm tra nháy mắt phải
        right = [landmarks[474], landmarks[478]] if num_landmarks > 478 else None
        if right and (right[0].y - right[1].y) < 0.004:
            blink_count_right += 1
            if blink_count_right == 1 and not program_paused:
                pyautogui.click(button='right')  # Click chuột phải
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

        for landmark in left:
            x_eye = int(landmark.x * frame_w)
            y_eye = int(landmark.y * frame_h)
            cv2.circle(annotated_frame, (x_eye, y_eye), 3, (0, 255, 255))

    else:
        print("Không phát hiện khuôn mặt.")

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

    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()
    cv2.putText(annotated_frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    cv2.putText(annotated_frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

    cv2.imshow("Eye Controlled Mouse", annotated_frame)

    # Kiểm tra phím 'q' để dừng chương trình
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Đang dừng chương trình...")
        break

webcam.release()
cv2.destroyAllWindows()