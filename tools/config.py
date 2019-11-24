import sys
import json
import os
import logging
logger = logging.getLogger(__name__)

CONFIG_FILE = "config.json"


def verify_config():
    if os.path.isfile(CONFIG_FILE) is False:
        logger.critical(CONFIG_FILE + " does not exist in root folder.")
        return False

    with open(CONFIG_FILE, "r") as cfgRead:
        try:
            json.load(cfgRead)
            return True
        except ValueError as e:
            logger.critical(CONFIG_FILE + " is not formatted properly {0}".format(e))
            return False


# load the json file as cfg, allows access as config.example.json. Stop on error.
def start_config():
    global cfg
    if verify_config():
        with open(CONFIG_FILE, "r") as cfgFile:
            cfg = json.load(cfgFile)
            logger.info(CONFIG_FILE + " loaded.")
            return True
    else:
        logger.critical(CONFIG_FILE + "Unable to start. Error in loading configuration file.")
        sys.exit(0)


def reload_config():
    global cfg
    if verify_config():
        del cfg
        with open(CONFIG_FILE, "r") as cfgFile:
            cfg = json.load(cfgFile)
            logger.info(CONFIG_FILE + " reloaded in place.")
            return True


start_config()


