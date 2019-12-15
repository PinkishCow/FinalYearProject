import time
from picamera import PiCamera


def run_still_example():

    camera = PiCamera(
        sensor_mode=5
    )
    camera.exposure_mode = "sports"
    camera.start_preview()
    time.sleep(10)
    camera.capture('test.jpg')
    camera.stop_preview()

