import datetime
import logging
import sys

logging.basicConfig(filename=datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info("Starting")
logger.info(sys.platform)


def invalid():
    print("Not a valid choice")

# https://stackoverflow.com/questions/19964603/creating-a-menu-in-python


def menu():
    if sys.platform.startswith('win32'):
        import training.cascade
        choices = {"1": ('Create background file', training.cascade.createbackgroundfile.start),
                   "2": ('Convert image tags', training.cascade.converttags.start),
                   "3": ('Augment images', training.cascade.augmentImages.start),
                   "Z": ('Exit', exit)}
    elif sys.platform.startswith('linux'):
        import examples
        choices = {"1": ('Create backgrounds', examples.imageLoadExample.test),
                   "Z": ('Exit', exit)}
    else:
        logging.error("Incorrect OS")
        logging.error(sys.platform)
        exit()

    for key in sorted(choices.keys()):
        print(key + ":" + choices[key][0])
    print("Please select a task")
    choices.get(input(), [None, invalid])[1]()


# TODO Face Example
# TODO OS Recognition
# TODO Multi System Communication
# TODO Basic Training and detection system

while True:
    menu()
