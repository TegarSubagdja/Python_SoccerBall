import tkinter as tk
from tkinter import messagebox
from ObjectDetection import ObjectDetection

# URL dari ESP32-CAM dan file HSV
esp32cam_url = "http://192.168.1.10/jpg"
data_url = "http://192.168.1.10/data"
hsv_file = 'hsv_vals.txt'

# Membuat instance ObjectDetection
object_detection = ObjectDetection(esp32cam_url, data_url, hsv_file)

def start_action():
    object_detection.mulai()
    messagebox.showinfo("Status", "Robot Aktif")

def stop_action():
    object_detection.berhenti()
    messagebox.showinfo("Status", "Robot Nonaktif")

# Membuat instance Tkinter
root = tk.Tk()
root.title("Remote")

# Menentukan ukuran jendela
root.geometry("300x200")

# Menambahkan label judul
title_label = tk.Label(root, text="Pengendali Robot", font=("Arial", 16))
title_label.pack(pady=10)

# Membuat tombol Start
start_button = tk.Button(root, text="Mulai", command=start_action, height=1, width=10)
start_button.pack(pady=10)

# Membuat tombol Stop
stop_button = tk.Button(root, text="Berhenti", command=stop_action, height=1, width=10)
stop_button.pack(pady=10)

# Menjalankan loop utama Tkinter
root.mainloop()
