import datetime
import logging
import sys
import os
import tools.config
import examples.picameraExample as example

logging.basicConfig(filename=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("Starting")
logging.info(sys.platform)
# whole program in here

example.run_cam_example()





# TODO Menu System
# TODO Face Example
# TODO OS Recognition
# TODO Multi System Communication
# TODO Basic Training and detection system
