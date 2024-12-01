import cv2
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock

class EyeTrackingApp(App):
    def build(self):
        self.tracking_widget = EyeTrackingWidget()
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.tracking_widget)
        return layout

class EyeTrackingWidget(Image):
    def __init__(self, **kwargs):
        super(EyeTrackingWidget, self).__init__(**kwargs)
        self.capture = cv2.VideoCapture(0)
        self.blink_count = 0
        self.start_time = None
        self.detected = False
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.flip(frame, 0)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, _ = frame.shape

            if not self.detected:
                self.start_time = time.time()
                self.detected = True
            elif time.time() - self.start_time >= 5:
                self.show_message("Mắt bạn đã nhìn vào điểm trong 5 giây!")
                self.detected = False

            buf = cv2.flip(frame_rgb, 0).tobytes()
            image_texture = Texture.create(size=(width, height), colorfmt='rgb')
            image_texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            self.texture = image_texture

    def show_message(self, message):
        self.parent.clear_widgets()
        self.parent.add_widget(Label(text=message, font_size='20sp'))

    def __del__(self):
        self.capture.release()

if __name__ == '__main__':
    EyeTrackingApp().run()
