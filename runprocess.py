import tkinter as tk
from PIL import Image, ImageTk
import cv2
from process import get_camera_frame, process_frame

root = tk.Tk()
root.title("Camera Interface")
root.geometry("900x600")
root.configure(bg='#1E2440')

camera_frame = tk.Label(root)
camera_frame.place(x=20, y=100, width=600, height=400)

side_frame = tk.Frame(root, bg='#1E2440')
side_frame.place(x=650, y=100)

user_icon = tk.Label(side_frame, text="👤", font=("Helvetica", 32), bg='#1E2440', fg='white')
user_icon.pack(pady=10)

user_name_label = tk.Label(side_frame, text="Hi, User", font=("Helvetica", 12), bg='#1E2440', fg='white')
user_name_label.pack(pady=10)

up_button = tk.Button(side_frame, text="⬆", font=("Helvetica", 24), bg='#1E2440', fg='white', width=4)
up_button.pack(pady=10)

down_button = tk.Button(side_frame, text="⬇", font=("Helvetica", 24), bg='#1E2440', fg='white', width=4)
down_button.pack(pady=10)

keyboard_button = tk.Button(side_frame, text="⌨", font=("Helvetica", 24), bg='#1E2440', fg='white', width=4)
keyboard_button.pack(pady=10)

cap = cv2.VideoCapture(0)

# Tăng độ phân giải camera để có hình ảnh rõ nét hơn
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

def update_camera():
    frame = get_camera_frame(cap)
    if frame is not None:
        processed_frame = process_frame(frame)  # Xử lý frame với Mediapipe
        cv2image = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        camera_frame.imgtk = imgtk
        camera_frame.configure(image=imgtk)

    camera_frame.after(10, update_camera)  # Cập nhật frame mỗi 10ms để tạo sự mượt mà

update_camera()

root.mainloop()

cap.release()
cv2.destroyAllWindows()
