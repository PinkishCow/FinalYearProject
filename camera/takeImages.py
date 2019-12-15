import time
import picamera
import os


def start():
    print("Please input folder name")
    folder = input()
    print("Please input image count")
    count = input()
    print("Taking {} images and saving them in a folder named {}".format(count, folder))
    path = os.path.join("images", folder)
    if os.path.exists(path):
        take_image_set(path, int(count))
    else:
        os.mkdir(path)
        take_image_set(path, int(count))


def take_image_set(path, count: int):
    for x in range(count):
        with picamera.PiCamera() as cam:
            time.sleep(.4)
            cam.resolution = (1024, 768)
            cam.start_preview()
            time.sleep(.1)
            cam.capture(os.path.join(path, str(count) + ".jpg"))

