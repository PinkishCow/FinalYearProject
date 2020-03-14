import asyncio
import logging
import json
import tools.config as config

# Every image source has same class
# Assign sources and detectors to IDs

logger = logging.getLogger(__name__)


class Server:

    def __init__(self, imagesource, detector):
        self.clientResults = None
        self.inputBlocker = asyncio.Event()
        self.detector = detector
        self.source = imagesource
        self.exitKeyPressed = False

    async def open_server(self):
        svr = await asyncio.start_server(self.receive_message, "192.168.4.1", 67676)

        async with svr:
            await svr.serve_forever()

    async def recognition_loop(self, writer: asyncio.StreamWriter):
        while not self.exitKeyPressed:
            self.inputBlocker.clear()
            self.clientResults = None
            writer.write(json.dumps("capture").encode())
            localresults = self.detector.recognise(self.source.getImage())
            await self.inputBlocker.wait()

    async def receive_message(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await reader.read()  # Reads all bytes when empty or -1, all examples seem to say you _must_ define a
        # size for some reason
        message = json.loads(data.decode())
        message_start = message[0]
        logging.debug("Received {0}".format(message))
        print("Received {0}".format(message))

        if message_start == "start":
            message_out = json.dumps(("setup", self.detector.id()))
            writer.write(message_out.encode())
        elif message_start == "error":
            logging.error("Received stop from client: {0}".format(message))
            message_out = json.dumps("stop")
            writer.write(message_out.encode())
            exit()
        elif message_start == "result":
            message_out = json.dumps("wait")
            writer.write(message_out.encode())
            self.clientResults = message[1]
        elif message_start == "ready":
            # Check if already exists sometime
            asyncio.create_task(self.recognition_loop(writer))
        else:
            # Throw exceptions here instead
            logging.error("Bad message returned: {0}, {1}".format(writer.get_extra_info("peername"), message))
            print("Bad message received, stopping")
            message_out = json.dumps("stop")
            writer.write(message_out.encode())
            exit()


class Client:

    def __init__(self, imagesource, detector):
        self.detector = detector
        self.source = imagesource
        self.reader = None
        self.writer = None
        self.receive_task = None  # receive message loop

    async def open_connection(self):
        self.reader, self.writer = asyncio.open_connection("192.168.4.1", 67676)

        start_message = json.dumps("start")
        self.writer.write(start_message.encode())

        data = await self.reader.read()
        msg = json.loads(data.decode())
        if msg[0] == "setup":
            await self.setup_detector(msg[1])
            self.writer.write(json.dumps("ready").encode())
        else:
            logging.error("No setup message received: {0}".format(msg))
        self.receive_task = asyncio.create_task(self.receive_message())

    async def receive_message(self):
        while True:
            data = await self.reader.read()
            msg = json.loads(data.decode())
            message_start = msg[0]
            logging.debug("Received {0}".format(msg))
            print("Received {0}".format(msg))

            if message_start == "capture":
                asyncio.create_task(self.capture())

    async def send_message(self, message):
        # more logic some other time, separated so the receiver can get straight back to working
        self.writer.write(message.encode())

    async def capture(self):
        results = self.detector.recognise(self.source.getImage())
        message = json.dumps(("result", results))
        await self.send_message(message)

    async def setup_detector(self, detectorid):
        # 1 = Cascade ver 1
        if detectorid == "1":
            import recognition.cascaderecognition
            recog = recognition.cascaderecognition.CascadeRecognition(config.cfg['pi']['cascade']['scale'],
                                                                      config.cfg['pi']['cascade']['neighbours'])
            recog.add_classifier(config.cfg['pi']['cascade']['cascades']['can'], "can")
            recog.add_classifier(config.cfg['pi']['cascade']['cascades']['cereal'], "cereal")
            recog.add_classifier(config.cfg['pi']['cascade']['cascades']['spray'], "spray")
            self.detector = recog
        elif detectorid == "2":
            exit()
