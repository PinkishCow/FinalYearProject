import time
from picamera import PiCamera


def run_video_example():

    camera = PiCamera(
        resolution=(1640, 922),
        sensor_mode=5,
        framerate=10
    )
    camera.exposure_mode = "sports"
    camera.start_preview()
    camera.start_recording('test.h264', resize=(1280, 720))
    camera.wait_recording(10)
    camera.stop_recording()
    camera.stop_preview()
    camera.close()
