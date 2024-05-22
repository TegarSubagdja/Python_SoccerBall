# ObjectDetection.py
import cvzone
from cvzone.ColorModule import ColorFinder
import cv2
import requests
import numpy as np
import threading

class ObjectDetection:
    def __init__(self, esp32cam_url, data_url, hsv_file):
        self.esp32cam_url = esp32cam_url
        self.data_url = data_url
        self.hsv_file = hsv_file
        self.hsvVals = self.read_hsv_vals()
        self.running = False
        self.thread = None
        self.myColorFinder = ColorFinder(False)

    def read_hsv_vals(self):
        local_vars = {}
        with open(self.hsv_file, 'r') as file:
            exec(file.read(), {}, local_vars)
        return local_vars['hsvVals']

    def get_image_from_esp32cam(self):
        try:
            response = requests.get(self.esp32cam_url)
            response.raise_for_status()  # Check if the request was successful
            img_array = np.array(bytearray(response.content), dtype=np.uint8)
            img = cv2.imdecode(img_array, -1)
            return img
        except requests.exceptions.RequestException as e:
            print(f"Failed to get image from ESP32-CAM: {e}")
            return None

    def moveDirection(self, direction):
        response = requests.get(f"{self.data_url}?value={direction}")
        if response.status_code == 200:
            print(f"Successfully sent value: {direction}")
        else:
            print(f"Failed to send value: {direction}, Status code: {response.status_code}")

    def detection_loop(self):
        while self.running:
            img = self.get_image_from_esp32cam()
            if img is None:
                print("Failed to get image from ESP32-CAM")
                continue

            imgColor, mask = self.myColorFinder.update(img, self.hsvVals)
            imgContour, contours = cvzone.findContours(img, mask)

            if contours:
                center_x = contours[0]['center'][0]
                center_y = contours[0]['center'][1]
                area = int(contours[0]['area'])
                print(f"Center X: {center_x}, Center Y: {center_y}, Area: {area}")

                if center_x < 635:
                    self.moveDirection(2)
                elif center_x > 645:
                    self.moveDirection(1)

            # cv2.imshow("ImageContour", imgContour)
            cv2.waitKey(1)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.detection_loop)
            self.thread.start()

    def stop(self):
        if self.running:
            self.running = False
            self.thread.join()
            cv2.destroyAllWindows()
