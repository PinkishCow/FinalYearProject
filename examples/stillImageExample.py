import time
from picamera import PiCamera


def run_still_example():

    camera = PiCamera(
        resolution=(1280, 720),
        sensor_mode=6
    )

    camera.start_preview()
    time.sleep(10)
    camera.capture('test.jpg')

