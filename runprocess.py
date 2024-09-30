import tkinter as tk
from PIL import Image, ImageTk
import cv2
from process import EyeTrackingProcessor  # Import class xử lý từ process.py

root = tk.Tk()
root.title("Camera Interface")
root.geometry("900x600")
root.configure(bg='#1E2440')

# Camera frame
camera_frame = tk.Label(root)
camera_frame.place(x=20, y=100, width=600, height=400)

# Side control frame
side_frame = tk.Frame(root, bg='#1E2440')
side_frame.place(x=650, y=100)

up_button = tk.Button(side_frame, text="⬆", font=("Helvetica", 24), bg='#1E2440', fg='white', width=4)
up_button.pack(pady=10)

down_button = tk.Button(side_frame, text="⬇", font=("Helvetica", 24), bg='#1E2440', fg='white', width=4)
down_button.pack(pady=10)

keyboard_button = tk.Button(side_frame, text="⌨", font=("Helvetica", 24), bg='#1E2440', fg='white', width=4)
keyboard_button.pack(pady=10)

# Eye Tracking Processor instance
processor = EyeTrackingProcessor()

# Open webcam
cap = cv2.VideoCapture(0)

def update_camera():
    ret, frame = cap.read()
    if ret:
        frame = cv2.flip(frame, 1)  # Flip the frame to match real-time movements
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB

        # Convert frame to ImageTk for displaying in Tkinter
        img = Image.fromarray(rgb_frame)
        imgtk = ImageTk.PhotoImage(image=img)
        camera_frame.imgtk = imgtk
        camera_frame.configure(image=imgtk)

        # Process the frame to detect eye movements
        processor.process_frame(frame, rgb_frame)

    # Update the frame every 10ms
    camera_frame.after(10, update_camera)

# Start updating the camera feed
update_camera()

# Handle window close event
def on_closing():
    cap.release()  # Release the webcam
    cv2.destroyAllWindows()  # Destroy OpenCV windows
    root.destroy()  # Close the Tkinter window

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
