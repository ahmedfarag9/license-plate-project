import time
from picamera2 import Picamera2

picam2 = Picamera2()
picam2.start()
picam2.capture_file("car.jpg")
picam2.stop()

print("Image captured successfully!")