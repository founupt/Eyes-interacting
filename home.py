import tkinter as tk
from PIL import Image, ImageTk
import cv2
import sys
import subprocess

user_name = sys.argv[1] if len(sys.argv) > 1 else "User"

root = tk.Tk()
root.title("Camera Interface")
root.geometry("900x600")
root.configure(bg='#1E2440')

# Khung để hiển thị camera
camera_frame = tk.Label(root)
camera_frame.place(x=20, y=100, width=600, height=400)

# Khung điều khiển bên phải
side_frame = tk.Frame(root, bg='#1E2440')
side_frame.place(x=650, y=100)

user_icon = tk.Label(side_frame, text="👤", font=("Helvetica", 32), bg='#1E2440', fg='white')
user_icon.pack(pady=10)

user_name_label = tk.Label(side_frame, text=f"Hi, {user_name}", font=("Helvetica", 12), bg='#1E2440', fg='white')
user_name_label.pack(pady=10)

# Các nút điều khiển
up_button = tk.Button(side_frame, text="⬆", font=("Helvetica", 24), bg='#1E2440', fg='white', width=4)
up_button.pack(pady=10)

down_button = tk.Button(side_frame, text="⬇", font=("Helvetica", 24), bg='#1E2440', fg='white', width=4)
down_button.pack(pady=10)

keyboard_button = tk.Button(side_frame, text="⌨", font=("Helvetica", 24), bg='#1E2440', fg='white', width=4)
keyboard_button.pack(pady=10)

# Nút Start Tracking (khởi chạy camera tracking)
def start_tracking():
    """Hàm khởi chạy mã xử lý camera."""
    subprocess.Popen(['python', 'camera_tracking.py'])  # Giả sử bạn lưu phần mã camera trong camera_tracking.py

start_button = tk.Button(side_frame, text="Start Tracking", font=("Helvetica", 16), bg='#1E2440', fg='white', command=start_tracking)
start_button.pack(pady=10)

# Nút Stop Tracking (dừng camera tracking)
def stop_tracking():
    """Hàm để dừng mã xử lý camera."""
    subprocess.Popen(['pkill', '-f', 'camera_tracking.py'])  # Dừng quá trình camera bằng lệnh pkill (chỉ hoạt động trên Unix)

stop_button = tk.Button(side_frame, text="Stop Tracking", font=("Helvetica", 16), bg='#1E2440', fg='white', command=stop_tracking)
stop_button.pack(pady=10)

# Hiển thị camera (live feed)
cap = cv2.VideoCapture(0)

def update_camera():
    ret, frame = cap.read()
    if ret:
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        camera_frame.imgtk = imgtk
        camera_frame.configure(image=imgtk)
    camera_frame.after(10, update_camera)  # Cập nhật hình ảnh sau mỗi 10ms

update_camera()

root.mainloop()

cap.release()
cv2.destroyAllWindows()
