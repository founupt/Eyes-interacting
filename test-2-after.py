import os
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import sys
import pyautogui
from test import TrackingFace

user_name = sys.argv[1] if len(sys.argv) > 1 else "User"

root = tk.Tk()
root.title("Camera Interface")
root.geometry("1000x700")
root.configure(bg='#1E2440')

tracking_active = False
tracking_face = None

camera_frame = tk.Label(root)
camera_frame.place(x=20, y=100, width=700, height=500)

side_frame = tk.Frame(root, bg='#1E2440')
side_frame.place(x=750, y=100)

user_icon = tk.Label(side_frame, text="👤", font=("Helvetica", 32), bg='#1E2440', fg='white')
user_icon.pack(pady=10)
user_name_label = tk.Label(side_frame, text=f"Hi, {user_name}", font=("Helvetica", 12), bg='#1E2440', fg='white')
user_name_label.pack(pady=10)

up_button = tk.Button(side_frame, text="⬆", font=("Helvetica", 24), bg='#1E2440', fg='white', width=4, command=lambda: pyautogui.scroll(10))
up_button.pack(pady=10)
down_button = tk.Button(side_frame, text="⬇", font=("Helvetica", 24), bg='#1E2440', fg='white', width=4, command=lambda: pyautogui.scroll(-10))
down_button.pack(pady=10)

cap = cv2.VideoCapture(0)

def stop_program(event=None):
    print("Stopping program...")
    global cap
    cap.release()
    cv2.destroyAllWindows()
    root.quit()

root.bind('<Escape>', stop_program)

def update_camera():
    global tracking_face
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (700, 500))
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

tracking_active = True
update_camera()

root.mainloop()

cap.release()
cv2.destroyAllWindows()
