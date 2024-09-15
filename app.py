import tkinter as tk
from tkinter import ttk

def scroll_up():
    print("Scrolling Up")

def scroll_down():
    print("Scrolling Down")

def close_app():
    root.destroy()

root = tk.Tk()
root.title("Camera Interface")
root.geometry("1000x600")
root.configure(bg="white")

# Màu nền khung camera
camera_bg_color = "#D9D9D9"  

# Khung camera ở giữa
camera_frame = ttk.Frame(root, width=600, height=400, relief="solid", style="CameraFrame.TFrame")
camera_frame.pack(pady=20, padx=20, expand=True)

camera_label = ttk.Label(camera_frame, text="CAMERA", font=("Arial", 24))
camera_label.pack(expand=True)

right_frame = ttk.Frame(root, padding=20)
right_frame.pack(side=tk.RIGHT)

button_up = ttk.Button(right_frame, text="↑", command=scroll_up, width=5)
button_up.pack(pady=20)


button_down = ttk.Button(right_frame, text="↓", command=scroll_down, width=5)
button_down.pack(pady=20)

close_button = ttk.Button(right_frame, text="X", command=close_app, width=5)
close_button.pack(pady=20)

style = ttk.Style()
style.configure("CameraFrame.TFrame", background=camera_bg_color)

# Nâng cao nút
for btn in [button_up, button_down, close_button]:
    btn.configure(style="CameraButton.TButton")

root.mainloop()