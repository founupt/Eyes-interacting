import cv2
import mediapipe as mp
import pyautogui
import time

class TrackingFace:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.screen_w = 1920
        self.screen_h = 1080
        self.last_x = self.screen_w // 2
        self.last_y = self.screen_h // 2

        self.blink_count_left = 0
        self.blink_count_right = 0
        self.double_blind_duration = 4
        self.double_blind_start_time = None
        self.face_mesh = self.mp_face_mesh.FaceMesh(refine_landmarks=True)

        # Khởi tạo biến thời gian nháy mắt
        self.start_time_blink_left = None
        self.start_time_blink_right = None

    def smooth_move(self, target_x, target_y, current_x, current_y, smoothing_factor=1):
        new_x = current_x + (target_x - current_x) * smoothing_factor
        new_y = current_y + (target_y - current_y) * smoothing_factor
        return int(new_x), int(new_y)

    def process_frame(self, frame):
        if frame is None:
            return None

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = self.face_mesh.process(rgb_frame)

        if output.multi_face_landmarks:
            landmarks = output.multi_face_landmarks[0].landmark

            left_pupil_x = int(landmarks[468].x * self.screen_w)
            left_pupil_y = int(landmarks[468].y * self.screen_h)
            right_pupil_x = int(landmarks[473].x * self.screen_w)
            right_pupil_y = int(landmarks[473].y * self.screen_h)

            target_x = (left_pupil_x + right_pupil_x) // 2
            target_y = (left_pupil_y + right_pupil_y) // 2

            target_x = max(0, min(target_x, self.screen_w - 1))
            target_y = max(0, min(target_y, self.screen_h - 1))

            self.last_x, self.last_y = self.smooth_move(target_x, target_y, self.last_x, self.last_y, smoothing_factor=0.5)
            pyautogui.moveTo(self.last_x, self.last_y)

            left_eye_closed = (landmarks[145].y - landmarks[159].y) < 0.004
            right_eye_closed = (landmarks[374].y - landmarks[386].y) < 0.004

            if left_eye_closed:
                self.blink_count_left += 1
                if self.blink_count_left == 1:
                    self.start_time_blink_left = time.time()
                if self.blink_count_left >= 2 and self.start_time_blink_left is not None and (time.time() - self.start_time_blink_left < 0.8):
                    pyautogui.click()
                    print('Double click chuột trái')
                    self.blink_count_left = 0
                elif self.blink_count_left == 1:
                    pyautogui.click()
                    print('Click chuột trái')
            else:
                self.blink_count_left = 0

            if right_eye_closed:
                self.blink_count_right += 1
                if self.blink_count_right == 1:
                    self.start_time_blink_right = time.time()
                if self.blink_count_right >= 2 and self.start_time_blink_right is not None and (time.time() - self.start_time_blink_right < 0.4):
                    pyautogui.click(button='right')
                    print('Double click chuột phải')
                    self.blink_count_right = 0
                elif self.blink_count_right == 1:
                    pyautogui.click(button='right')
                    print('Click chuột phải')
            else:
                self.blink_count_right = 0

            if left_eye_closed and right_eye_closed:
                if self.double_blind_start_time is None:
                    self.double_blind_start_time = time.time()
                elif time.time() - self.double_blind_start_time >= self.double_blind_duration:
                    print("Stopping program due to both eyes being closed.")
                    return None
            else:
                self.double_blind_start_time = None

            gaze_text = self.get_gaze_direction(left_pupil_x, left_pupil_y)
            cv2.putText(frame, gaze_text, (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1.5, (147, 58, 31), 2)

        return frame

    def get_gaze_direction(self, x, y):
        center_width = 200
        center_height = 200
        center_x_start = (self.screen_w - center_width) / 2
        center_x_end = center_x_start + center_width
        center_y_start = (self.screen_h - center_height) / 2
        center_y_end = center_y_start + center_height

        if y < self.screen_h / 2:
            if x < self.screen_w / 3:
                return "Moving Up Left"
            elif x < 2 * self.screen_w / 3:
                return "Moving Up Middle"
            else:
                return "Moving Up Right"
        else:
            if x < self.screen_w / 3:
                return "Moving Down Left"
            elif x < 2 * self.screen_w / 3:
                return "Moving Down Middle"
            else:
                return "Moving Down Right"

        if (x >= center_x_start and x <= center_x_end) and (y >= center_y_start and y <= center_y_end):
            return "Center"

    def __del__(self):
        self.face_mesh.close()