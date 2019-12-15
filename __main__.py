import datetime
import logging
import sys
import examples.imageLoadExample

logging.basicConfig(filename=datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("Starting")
logging.info(sys.platform)
# whole program in here

choices = {'a': examples.imageLoadExample.test}
for key in choices.keys():
    print(key)
print("Please select a task")
choices[input()]()














# TODO Menu System
# TODO Face Example
# TODO OS Recognition
# TODO Multi System Communication
# TODO Basic Training and detection system
