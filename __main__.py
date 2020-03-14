import datetime
import logging
import sys
import asyncio

logging.basicConfig(filename=datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info("Starting")
logger.info(sys.platform)


def invalid():
    print("Not a valid choice")

# https://stackoverflow.com/questions/19964603/creating-a-menu-in-python


def startup():
    if sys.platform.startswith('linux'):
        x = False
        while not x:
            inp = input("Connect to second system? (Y/N)")
            inp.lower()
            if inp == 'n':
                x = True
                while True:
                    solomenu()
            elif inp == 'y':
                inpx = input("Host?")
                inpx.lower()
                if inpx == 'y':
                    x = True
                    server()
                elif inpx == 'n':
                    x = True
                    client()
                else:
                    invalid()
            else:
                invalid()


# def server():
#     import socket
#     host = "192.168.4.1"
#     port = 67676
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
#         sock.bind((host, port))
#         sock.listen()
#         conn, addr = sock.accept()
#         with conn:
#             print("Connected with " + addr)
#             logger.info("Connected with " + addr)
#             conn.send(b'Connected at %(DT)s' % {b'DT': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
#
#
# def client():
#     import socket
#     host = "192.168.4.1"
#     port = 67676
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
#         sock.connect((host, port))
#         rec = sock.recv(1024)
#         print(repr(rec))
#         logger.info(repr(rec))


async def solomenu():
    if sys.platform.startswith('win32'):
        import training.cascade
        import recognition
        choices = {"1": ('Create background file', training.cascade.createbackgroundfile.start),
                   "2": ('Convert image tags', training.cascade.converttags.start),
                   "3": ('Cascade tests', recognition.cascaderecognition.test_menu),
                   "Z": ('Exit', exit)}
    elif sys.platform.startswith('linux'):
        import recognition
        choices = {"1": ('Cascade tests', recognition.cascaderecognition.test_menu),
                   "Z": ('Exit', exit)}
    else:
        logging.error("Incorrect OS")
        logging.error(sys.platform)
        exit()

    for key in sorted(choices.keys()):
        print(key + ":" + choices[key][0])
    print("Please select a task")
    choices.get(input(), [None, invalid])[1]()


# TODO Multi System Communication
# TODO Cleanup
# TODO Recognition correctness statistics
# TODO Tensorflow setup and testing & OpenCV 4 build with CUDA

startup()
