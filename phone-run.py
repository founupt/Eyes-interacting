import cv2
import mediapipe as mp
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.uix.popup import Popup


class EyeTrackingApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        # Widget hiển thị video
        self.tracking_widget = EyeTrackingWidget()
        layout.add_widget(self.tracking_widget)

        # Label hiển thị trạng thái
        self.status_label = Label(text="Trạng thái: Đang theo dõi...", font_size='18sp', size_hint=(1, 0.1))
        layout.add_widget(self.status_label)

        # Gắn label trạng thái vào widget xử lý video
        self.tracking_widget.status_label = self.status_label

        return layout


class EyeTrackingWidget(Image):
    def __init__(self, **kwargs):
        super(EyeTrackingWidget, self).__init__(**kwargs)
        self.capture = cv2.VideoCapture(0)
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
        self.blink_count = 0
        self.status_label = None
        self.popup_shown = False  # Tránh hiện popup nhiều lần

        # Cập nhật khung hình 30 FPS
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def update(self, dt):
        ret, frame = self.capture.read()
        if not ret:
            return

        # Lật và xử lý khung hình
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.mp_face_mesh.process(rgb_frame)

        if result.multi_face_landmarks:
            landmarks = result.multi_face_landmarks[0].landmark
            left_eye_ratio = landmarks[145].y - landmarks[159].y
            right_eye_ratio = landmarks[374].y - landmarks[386].y

            # Phát hiện nháy mắt
            if left_eye_ratio < 0.004 or right_eye_ratio < 0.004:
                self.blink_count += 1
                if self.blink_count == 2:  # Nháy đúp
                    self.show_message("Nháy mắt đôi! Click chuột.")
                    self.blink_count = 0
            else:
                self.blink_count = 0

        # Hiển thị khung hình trên giao diện Kivy
        buf = cv2.flip(rgb_frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
        texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        self.texture = texture

    def show_message(self, message):
        """Hiển thị popup và cập nhật trạng thái."""
        if self.status_label:
            self.status_label.text = f"Trạng thái: {message}"

        # Hiện popup nếu chưa hiện
        if not self.popup_shown:
            self.popup_shown = True
            popup = Popup(title="Thông báo", content=Label(text=message), size_hint=(0.6, 0.3))
            popup.bind(on_dismiss=self.reset_popup_flag)
            popup.open()

    def reset_popup_flag(self, instance):
        """Đặt lại cờ khi popup bị đóng."""
        self.popup_shown = False

    def __del__(self):
        """Giải phóng tài nguyên camera khi thoát ứng dụng."""
        self.capture.release()


if __name__ == '__main__':
    EyeTrackingApp().run()
