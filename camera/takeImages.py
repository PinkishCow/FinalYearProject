import time
import picamera
import os


def take_image_set(folder, count):
    with picamera.PiCamera() as cam:
        for x in range(count):
            time.sleep(.4)
            cam.resolution = (1024, 768)
            cam.start_preview()
            time.sleep(.1)
            cam.capture(os.path.join("images", folder, count + ".jpg"))

