import cv2
import mediapipe as mp
import pyautogui
import time
import joblib

class TrackingFace:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.screen_w = 1920
        self.screen_h = 1080
        self.last_x = self.screen_w // 2
        self.last_y = self.screen_h // 2

        self.face_mesh = self.mp_face_mesh.FaceMesh(refine_landmarks=True)

        self.model = joblib.load("eye_tracking_model.pkl")

        self.blink_count_left = 0
        self.blink_count_right = 0
        self.start_time_blink_left = None
        self.start_time_blink_right = None

        self.double_blind_duration = 4
        self.double_blind_start_time = None

    def smooth_move(self, target_x, target_y, current_x, current_y, smoothing_factor=0.5):
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

      
            input_data = [[left_pupil_x, left_pupil_y, right_pupil_x, right_pupil_y]]
            prediction = self.model.predict(input_data)
            left_eye_closed = bool(prediction[0][0])
            right_eye_closed = bool(prediction[0][1])

        
            target_x = (left_pupil_x + right_pupil_x) // 2
            target_y = (left_pupil_y + right_pupil_y) // 2
            target_x = max(0, min(target_x, self.screen_w - 1))
            target_y = max(0, min(target_y, self.screen_h - 1))
            self.last_x, self.last_y = self.smooth_move(target_x, target_y, self.last_x, self.last_y)
            pyautogui.moveTo(self.last_x, self.last_y)

     
            if left_eye_closed:
                if self.blink_count_left == 0:
                    self.start_time_blink_left = time.time()
                self.blink_count_left += 1
                if self.blink_count_left >= 2 and time.time() - self.start_time_blink_left < 0.8:
                    pyautogui.click()
                    print('Double click chuột trái')
                    self.blink_count_left = 0
                elif self.blink_count_left == 1 and time.time() - self.start_time_blink_left > 0.5:
                    pyautogui.click()
                    print('Click chuột trái')
                    self.blink_count_left = 0
            else:
                self.blink_count_left = 0

            if right_eye_closed:
                if self.blink_count_right == 0:
                    self.start_time_blink_right = time.time()
                self.blink_count_right += 1
                if self.blink_count_right >= 2 and time.time() - self.start_time_blink_right < 0.4:
                    pyautogui.click(button='right')
                    print('Double click chuột phải')
                    self.blink_count_right = 0
                elif self.blink_count_right == 1 and time.time() - self.start_time_blink_right > 0.5:
                    pyautogui.click(button='right')
                    print('Click chuột phải')
                    self.blink_count_right = 0
            else:
                self.blink_count_right = 0

            if left_eye_closed and right_eye_closed:
                if self.double_blind_start_time is None:
                    self.double_blind_start_time = time.time()
                elif time.time() - self.double_blind_start_time >= self.double_blind_duration:
                    print("Stopping program due to both eyes being closed.")
                    return None
                else:
                    pyautogui.press("down")
                    print("Scroll down")
            else:
                self.double_blind_start_time = None
                pyautogui.press("up")
                print("Scroll up")

        return frame

    def __del__(self):
        self.face_mesh.close()

def main():
    cap = cv2.VideoCapture(0)
    tracker = TrackingFace()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        processed_frame = tracker.process_frame(frame)
        if processed_frame is None:
            break

        cv2.imshow("Eye Tracking", processed_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting program.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
