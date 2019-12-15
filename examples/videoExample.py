import time
from picamera import PiCamera


def run_still_example():

    camera = PiCamera(
        sensor_mode=5
    )
    camera.exposure_mode = "sports"
    camera.start_preview()
    camera.start_recording('test.h264')
    camera.wait_recording(10)
    camera.capture('test.jpg', use_video_port=True)
    camera.wait_recording(10)
    camera.stop_recording()
    camera.stop_preview()
