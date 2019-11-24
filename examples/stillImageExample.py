import time
import picamera

with picamera.PiCamera as cam:
    cam.resolution = (1024, 768)
    cam.start_preview()
    time.sleep(.1)
    cam.capture("wow.jpg")
