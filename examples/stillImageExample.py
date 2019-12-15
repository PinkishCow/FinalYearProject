import time
from picamera import PiCamera


def run_still_example():

    camera = PiCamera(
        sensor_mode=7
    )

    camera.start_preview()
    time.sleep(10)
    camera.capture('test.jpg')
    camera.stop_preview()

