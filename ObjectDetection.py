import cvzone
from cvzone.ColorModule import ColorFinder
import cv2
import requests
import numpy as np
import threading
import time

class ObjectDetection:
    def __init__(self, esp32cam_url, data_url, hsv_file):
        self.esp32cam_url = esp32cam_url
        self.data_url = data_url
        self.hsv_file = hsv_file
        self.hsvVals = self.baca_hsv_vals()
        self.running = False
        self.thread = None  # Objek Thread
        self.lock = threading.Lock()  # Tambahkan kunci untuk menghindari konflik
        self.myColorFinder = ColorFinder(False)

    def baca_hsv_vals(self):
        local_vars = {}
        with open(self.hsv_file, 'r') as file:
            exec(file.read(), {}, local_vars)
        return local_vars['hsvVals']

    def ambil_gambar_dari_esp32cam(self):
        try:
            response = requests.get(self.esp32cam_url, timeout=1)  # Tambahkan timeout 1 detik
            response.raise_for_status()  # Memeriksa apakah permintaan berhasil
            img_array = np.array(bytearray(response.content), dtype=np.uint8)
            img = cv2.imdecode(img_array, -1)
            return img
        except requests.exceptions.RequestException as e:
            print(f"Gagal mengambil gambar dari ESP32-CAM: {e}")
            return None

    def kirimArah(self, arah):
        try:
            response = requests.get(f"{self.data_url}?value={arah}")
            response.raise_for_status()
            print(f"Berhasil mengirim nilai: {arah}")
        except requests.exceptions.RequestException as e:
            print(f"Gagal mengirim nilai: {arah}, {e}")

    def detection_loop(self):
        while self.running:
            start_time = time.time()
            img = None
            with self.lock:  # Mengunci sebelum mengambil gambar
                img = self.ambil_gambar_dari_esp32cam()
            if img is None:
                print("Gagal mengambil gambar dari ESP32-CAM, menunggu 10 detik sebelum mencoba lagi")
                time.sleep(10)
                continue

            imgColor, mask = self.myColorFinder.update(img, self.hsvVals)
            imgContour, contours = cvzone.findContours(img, mask)

            if contours:
                center_x = contours[0]['center'][0]
                center_y = contours[0]['center'][1]
                area = int(contours[0]['area'])
                print(f"Center X: {center_x}, Center Y: {center_y}, Area: {area}")

                with self.lock: 
                    if center_x < 630:
                        self.kirimArah(2)
                    elif center_x > 640:
                        self.kirimArah(1)
                    else:
                        self.kirimArah(0)
            else:
                self.kirimArah(3)

            # Mengubah ukuran gambar menjadi setengah
            imgContour_resized = cv2.resize(imgContour, (imgContour.shape[1] // 2, imgContour.shape[0] // 2))

            cv2.imshow("ImageContour", imgContour_resized)
            cv2.waitKey(1)

    def mulai(self):
        if not self.running:
            self.running = True
            # Membuat dan memulai loop deteksi dalam thread baru
            self.thread = threading.Thread(target=self.detection_loop)
            self.thread.start()

    def berhenti(self):
        if self.running:
            self.running = False
            # Menunggu thread selesai
            self.thread.join()
            cv2.destroyAllWindows()
