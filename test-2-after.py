import os
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import sys
from test import TrackingFace

user_name = sys.argv[1] if len(sys.argv) > 1 else "User"

root = tk.Tk()
root.title("Camera Interface")
root.geometry("1000x700")  
root.configure(bg='#1E2440')

tracking_active = False
tracking_face = None

# Mở rộng kích thước khung camera
camera_frame = tk.Label(root)
camera_frame.place(x=20, y=100, width=700, height=500)  

side_frame = tk.Frame(root, bg='#1E2440')
side_frame.place(x=750, y=100)

user_icon = tk.Label(side_frame, text="👤", font=("Helvetica", 32), bg='#1E2440', fg='white')
user_icon.pack(pady=10)

user_name_label = tk.Label(side_frame, text=f"Hi, {user_name}", font=("Helvetica", 12), bg='#1E2440', fg='white')
user_name_label.pack(pady=10)

up_button = tk.Button(side_frame, text="⬆", font=("Helvetica", 24), bg='#1E2440', fg='white', width=4)
up_button.pack(pady=10)

down_button = tk.Button(side_frame, text="⬇", font=("Helvetica", 24), bg='#1E2440', fg='white', width=4)
down_button.pack(pady=10)

keyboard_button = tk.Button(side_frame, text="⌨", font=("Helvetica", 24), bg='#1E2440', fg='white', width=4)
keyboard_button.pack(pady=10)

cap = cv2.VideoCapture(0)

def update_camera():
    global tracking_face
    ret, frame = cap.read()
    if ret:
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

def start_tracking():
    global tracking_active
    tracking_active = True
    start_button.config(state=tk.DISABLED)  # Vô hiệu hóa nút "Start Tracking"
    stop_button.config(state=tk.NORMAL)    # Kích hoạt nút "Stop Tracking"

def stop_tracking():
    global tracking_active, tracking_face
    tracking_active = False
    tracking_face = None
    start_button.config(state=tk.NORMAL)   # Kích hoạt lại nút "Start Tracking"
    stop_button.config(state=tk.DISABLED)  # Vô hiệu hóa nút "Stop Tracking"

# Thêm nút Start và Stop Tracking
start_button = tk.Button(side_frame, text="Start Tracking", font=("Helvetica", 16), bg='#1E2440', fg='white',
                         command=start_tracking)
start_button.pack(pady=10)

stop_button = tk.Button(side_frame, text="Stop Tracking", font=("Helvetica", 16), bg='#1E2440', fg='white',
                        command=stop_tracking)
stop_button.pack(pady=10)

# Gọi hàm start_tracking sau khi các nút đã được tạo
start_tracking()

update_camera()

root.mainloop()

cap.release()
cv2.destroyAllWindows()
