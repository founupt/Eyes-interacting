import tkinter as tk
from PIL import Image, ImageTk
import cv2
import pyautogui
from test import TrackingFace

root = tk.Tk()
root.title("Mobile Camera Interface")
root.geometry("360x640")  

camera_frame = tk.Label(root, bg="black")
camera_frame.pack(fill=tk.BOTH, expand=True)

cap = cv2.VideoCapture(0)
tracking_active = True
tracking_face = None

def update_camera():
    global tracking_face
    ret, frame = cap.read()
    if ret:
        # Resize cho phù hợp màn hình điện thoại
        camera_w = camera_frame.winfo_width()
        camera_h = camera_frame.winfo_height()
        frame = cv2.resize(frame, (camera_w, camera_h))

        if tracking_active:
            if tracking_face is None:
                tracking_face = TrackingFace()
            frame = tracking_face.process_frame(frame)

        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        camera_frame.imgtk = imgtk
        camera_frame.configure(image=imgtk)

    camera_frame.after(10, update_camera)

def stop_program(event=None):
    global cap
    cap.release()
    cv2.destroyAllWindows()
    root.quit()

root.bind('<Escape>', stop_program)
update_camera()
root
