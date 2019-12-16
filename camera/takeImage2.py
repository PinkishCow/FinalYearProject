import time
import picamera
import os


frames = 10
folder = ""


def start():
    print("Please input folder name")
    folder = input()
    print("Please input image count")
    frames = input()
    print("Taking {} images and saving them in a folder named {}".format(frames, folder))
    folder = os.path.join("images", folder)
    if os.path.exists(folder):
        take_image_set()
    else:
        os.mkdir(folder)
        take_image_set()


def filenames():
    frame = 0
    while frame < frames:
        yield os.path.join(folder, "image%02d.jpg" % frame)
        print(os.path.join(folder, "image%02d.jpg" % frame))
        frame += 1


def take_image_set():
    with picamera.PiCamera() as camera:
        camera.resolution = (1024, 768)
        camera.framerate = 5
        camera.start_preview()
        time.sleep(1)
        begin = time.time()
        camera.capture_sequence(filenames(), use_video_port=True)
        finish = time.time()
        print("Captured %d frames at %.2ffps" %(frames, frames / (finish - begin)))
