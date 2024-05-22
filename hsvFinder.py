import cvzone
from cvzone.ColorModule import ColorFinder
import cv2
import socket
import requests
import numpy as np

class hsvFinder:
    def __init__(self, url, server_address_port):
        self.esp32cam_url = url
        self.server_address_port = server_address_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.hsvVals = {'hmin': 0, 'smin': 0, 'vmin': 0, 'hmax': 179, 'smax': 255, 'vmax': 255}
        self.myColorFinder = ColorFinder(False)
        self.setup_trackbars()

    def set_values(self, trackbar_vals):
        self.hsvVals = {'hmin': trackbar_vals[0], 'smin': trackbar_vals[1], 'vmin': trackbar_vals[2],
                        'hmax': trackbar_vals[3], 'smax': trackbar_vals[4], 'vmax': trackbar_vals[5]}
        self.save_hsv_vals('hsv_vals.txt')

    def save_hsv_vals(self, filename):
        with open(filename, 'w') as file:
            file.write("hsvVals = {\n")
            for key, value in self.hsvVals.items():
                file.write(f"    '{key}': {value},\n")
            file.write("}\n")

    def get_image_from_esp32cam(self):
        response = requests.get(self.esp32cam_url)
        img_array = np.array(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, -1)
        return img

    def get_image(self):
        img = self.get_image_from_esp32cam()
        if img is not None:
            h, w, _ = img.shape
        else:
            h, w = 0, 0
        return img, h, w

    def setup_trackbars(self):
        cv2.namedWindow("Trackbars")
        cv2.resizeWindow("Trackbars", 640, 240)
        cv2.createTrackbar("Hue Min", "Trackbars", self.hsvVals['hmin'], 179, lambda x: self.update_values())
        cv2.createTrackbar("Saturation Min", "Trackbars", self.hsvVals['smin'], 255, lambda x: self.update_values())
        cv2.createTrackbar("Value Min", "Trackbars", self.hsvVals['vmin'], 255, lambda x: self.update_values())
        cv2.createTrackbar("Hue Max", "Trackbars", self.hsvVals['hmax'], 179, lambda x: self.update_values())
        cv2.createTrackbar("Saturation Max", "Trackbars", self.hsvVals['smax'], 255, lambda x: self.update_values())
        cv2.createTrackbar("Value Max", "Trackbars", self.hsvVals['vmax'], 255, lambda x: self.update_values())

    def update_values(self):
        self.set_values([cv2.getTrackbarPos("Hue Min", "Trackbars"),
                         cv2.getTrackbarPos("Saturation Min", "Trackbars"),
                         cv2.getTrackbarPos("Value Min", "Trackbars"),
                         cv2.getTrackbarPos("Hue Max", "Trackbars"),
                         cv2.getTrackbarPos("Saturation Max", "Trackbars"),
                         cv2.getTrackbarPos("Value Max", "Trackbars")])

    def process_image(self):
        img, h, w = self.get_image()
        if img is None:
            print("Failed to get image from ESP32-CAM")
            return None

        imgColor, mask = self.myColorFinder.update(img, self.hsvVals)
        imgContour, contours = cvzone.findContours(img, mask)

        if contours:
            data = contours[0]['center'][0], \
                   h - contours[0]['center'][1], \
                   int(contours[0]['area'])
            print(data)
            self.sock.sendto(str.encode(str(data)), self.server_address_port)

        imgContour = cv2.resize(imgContour, (0, 0), None, 0.5, 0.5)
        cv2.imshow("ImageContour", imgColor)
        cv2.waitKey(1)

    def run(self):
        while True:
            self.process_image()
