from picamera import PiCamera
import numpy as np


class PiCameraInput:
    def __init__(self, height, width, fps, exposure):
        self.camera = PiCamera()
        self.camera.resolution = (width, height)
        self.camera.framerate = fps
        self.camera.rotation = 180
        self.camera.shutter_speed = exposure
        self.height = height
        self.width = width

    def getImage(self):
        #  From picamera documentation https://picamera.readthedocs.io/en/release-1.10/recipes1.html
        image = np.empty((self.height * self.width * 3,), dtype=np.uint8)
        self.camera.capture(image, 'bgr')
        image = image.reshape((self.height, self.width, 3))
        return image
