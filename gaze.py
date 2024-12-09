import cv2
import mediapipe as mp
import pyautogui
import time
from gaze_tracking import GazeTracking

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
        self.start_time_blink_left = None
        self.start_time_blink_right = None
        self.scroll_timer = 0
        self.start_time_gaze = None
        self.gaze = GazeTracking()  # Initialize GazeTracking

    def smooth_move(self, target_x, target_y, current_x, current_y, smoothing_factor= 0.2):
        new_x = current_x + (target_x - current_x) * smoothing_factor
        new_y = current_y + (target_y - current_y) * smoothing_factor
        return int(new_x), int(new_y)

    def process_frame(self, frame):
        if frame is None:
            return None
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.gaze.refresh(frame_rgb)  # Refresh gaze tracking
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = self.face_mesh.process(rgb_frame)

        gaze_text = ""  # Variable to store gaze direction text

        if self.gaze.is_blinking():
            gaze_text = "Blinking"
        elif self.gaze.is_right():
            gaze_text = "Looking Right"
        elif self.gaze.is_left():
            gaze_text = "Looking Left"
        elif self.gaze.is_center():
            gaze_text = "Looking Center"
        
        # Add gaze text to frame for visualization
        cv2.putText(frame, gaze_text, (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1.5, (147, 58, 31), 2)

        if output.multi_face_landmarks:
            landmarks = output.multi_face_landmarks[0].landmark
            left_pupil_x = int(landmarks[468].x * self.screen_w)
            left_pupil_y = int(landmarks[468].y * self.screen_h)
            right_pupil_x = int(landmarks[473].x * self.screen_w)
            right_pupil_y = int(landmarks[473].y * self.screen_h)

            left_iris = [landmarks[474], landmarks[475], landmarks[476], landmarks[477]]
            right_iris = [landmarks[469], landmarks[470], landmarks[471], landmarks[472]]

            left_iris_x = int(sum([p.x for p in left_iris]) / len(left_iris) * self.screen_w)
            left_iris_y = int(sum([p.y for p in left_iris]) / len(left_iris) * self.screen_h)
            right_iris_x = int(sum([p.x for p in right_iris]) / len(right_iris) * self.screen_w)
            right_iris_y = int(sum([p.y for p in right_iris]) / len(right_iris) * self.screen_h)

            target_x = (left_iris_x + right_iris_x) // 2
            target_y = (left_iris_y + right_iris_y) // 2

            target_x = max(0, min(target_x, self.screen_w - 1))
            target_y = max(0, min(target_y, self.screen_h - 1))

            self.last_x, self.last_y = self.smooth_move(target_x, target_y, self.last_x, self.last_y, smoothing_factor=1)
            pyautogui.moveTo(self.last_x, self.last_y)

            # Eye closing detection logic
            face_height = abs(landmarks[10].y - landmarks[152].y)
            left_eye_closed = (landmarks[145].y - landmarks[159].y) < (0.02 * face_height)
            right_eye_closed = (landmarks[374].y - landmarks[386].y) < (0.02 * face_height)

            # Process blinks and simulate clicks
            self.handle_blinks(left_eye_closed, right_eye_closed)

            # Scroll based on gaze direction (keeping original logic intact)
            self.handle_gaze_based_scroll(target_x, target_y)

        return frame

    def handle_blinks(self, left_eye_closed, right_eye_closed):
        if left_eye_closed and not right_eye_closed:
            self.process_left_blink()
        elif right_eye_closed and not left_eye_closed:
            self.process_right_blink()
        elif left_eye_closed and right_eye_closed:
            self.handle_double_blink()

    def process_left_blink(self):
        if self.start_time_blink_left is None:
            self.start_time_blink_left = time.time()  
            self.blink_count_left = 1
        else:
            elapsed_time = time.time() - self.start_time_blink_left
            if elapsed_time < 0.4: 
                self.blink_count_left += 1
                if self.blink_count_left == 2:
                    print(f'Double-click chuột trái tại ({self.last_x}, {self.last_y})')
                    pyautogui.doubleClick()  
                    self.blink_count_left = 0
                    self.start_time_blink_left = None
            else:  
                print(f'Click chuột trái tại ({self.last_x}, {self.last_y})')
                pyautogui.click()
                self.blink_count_left = 0
                self.start_time_blink_left = None

    def process_right_blink(self):
        if self.start_time_blink_right is None:
            self.start_time_blink_right = time.time()  
            self.blink_count_right = 1
        else:
            elapsed_time = time.time() - self.start_time_blink_right
            if elapsed_time < 0.4:  
                self.blink_count_right += 1
                if self.blink_count_right == 2:
                    print(f'Double-click chuột phải tại ({self.last_x}, {self.last_y})')
                    pyautogui.doubleClick(button='right')  
                    self.blink_count_right = 0
                    self.start_time_blink_right = None
            else:  
                print(f'Click chuột phải tại ({self.last_x}, {self.last_y})')
                pyautogui.click(button='right')
                self.blink_count_right = 0
                self.start_time_blink_right = None

    def handle_double_blink(self):
        self.blink_count_left = 0
        self.blink_count_right = 0
        if self.double_blind_start_time is None:
            self.double_blind_start_time = time.time()
        elif time.time() - self.double_blind_start_time >= self.double_blind_duration:
            print("Stopping program due to both eyes being closed.")
            exit()
        else:
            self.double_blind_start_time = None

    def handle_gaze_based_scroll(self, target_x, target_y):
        # Scroll down when looking downward
        if target_y > self.screen_h / 2:
            if abs(target_y - self.last_y) < 100:  # Ensure there is some motion
                self.scroll_down()
        # Scroll up when looking upward
        elif target_y < self.screen_h / 2:
            if abs(target_y - self.last_y) < 100:  # Ensure there is some motion
                self.scroll_up()

    def scroll_down(self):
        for i in range(3):  
            pyautogui.scroll(-200)  
            time.sleep(0.02)  
        print("Cuộn xuống")

    def scroll_up(self):
        for i in range(3):  
            pyautogui.scroll(200)  
            time.sleep(0.02)  
        print("Cuộn lên")

    def __del__(self):
        self.face_mesh.close()

