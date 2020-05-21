import asyncio
import json
from recognition.cascaderecognition import CascadeRecognition
import os
from recognition.picamerain import PiCameraInput


def server_cascade_setup():
    cascade_path = "/home/pi/FinalYearProject/camera/cas"
    scale = 1.4
    neighbours = 20
    size = "3030"
    recog = CascadeRecognition(scale, neighbours)
    for item in os.listdir(os.path.join(cascade_path, size)):
        recog.add_classifier(os.path.join(cascade_path, size, item, "cascade.xml"), item)
    recog.toggle_clean(True)
    return recog


class Main:
    def __init__(self, ip, secondaryip):
        self.secondaryResults = []
        self.secondaryWaiting = asyncio.Event()
        self.secondaryComplete = asyncio.Event()
        self.detector = server_cascade_setup()  # Hard coded since TF isn't available
        self.source = PiCameraInput(768, 1024, 5, 30000)
        self.exitKeyPressed = False
        self.ip = ip
        self.secondaryip = secondaryip

    async def open_server(self):
        svr = await asyncio.start_server(self.receive_message, self.ip, 6767)

        async with svr:
            await svr.serve_forever()

    async def recognition_loop(self):
        while not self.exitKeyPressed:
            self.secondaryResults = []
            await self.secondaryWaiting.wait()
            self.secondaryWaiting.clear()
            await self.send_message(json.dumps("capture"))
            localresults = self.detector.recognise(self.source.getImage())
            await self.secondaryComplete.wait()
            self.secondaryComplete.clear()
            final_matches = []
            all_matches = localresults + self.secondaryResults
            done_names = []
            for match in all_matches:
                if not match[0] in done_names:
                    top_match = match
                    done_names.append(match[0])
                    for compare in all_matches:
                        if compare[0] == top_match[0]:
                            if compare[1][2] >= top_match[1][2]:
                                top_match = compare
                    final_matches.append(top_match)
            print(final_matches)  # Put through present_image if on system with a desktop active

    async def send_message(self, message):
        reader, writer = await asyncio.open_connection(self.secondaryip, 6767)
        writer.write(message.encode())
        data = await reader.read()
        message_in = json.loads(data.decode())
        print(message_in)
        message_start = message_in[0]
        if not message_start == "ok":
            print("Response error")
            print(message_in)
            exit()
        writer.close()

    async def receive_message(self, reader, writer):
        print("Message In")

        data = await reader.read()
        print(data)
        message = json.loads(data.decode())
        message_start = message[0]
        print("Received {0}".format(message))

        if message_start == "start":
            message_out = json.dumps("ok")
            writer.write(message_out.encode())
            await self.send_message(json.dumps("setup"))
        elif message_start == "error":
            message_out = json.dumps("stop")
            writer.write(message_out.encode())
            exit()
        elif message_start == "result":
            message_out = json.dumps("ok")
            writer.write(message_out.encode())
            self.secondaryResults = message[1]
            self.secondaryComplete.set()
            await self.send_message(json.dumps("wait"))
        elif message_start == "waiting":
            message_out = json.dumps("ok")
            writer.write(message_out.encode())
            self.secondaryWaiting.set()
        elif message_start == "ready":
            asyncio.create_task(self.recognition_loop())
        elif message_start == "test":
            print("Test successful")
        elif message_start == "stop":
            print("stopping")
            exit()
        else:
            print("Bad message received, stopping")
            message_out = json.dumps("stop")
            writer.write(message_out.encode())
            exit()
        writer.close()


class Secondary:
    def __init__(self, ip, mainip):
        self.waiting = asyncio.Event()
        self.detector = server_cascade_setup()  # Hard coded since TF isn't available
        self.source = PiCameraInput(768, 1024, 5, 30000)
        self.exitKeyPressed = False
        self.ip = ip
        self.mainip = mainip

    async def open_server(self):
        svr = await asyncio.start_server(self.receive_message, self.ip, 6767)

        async with svr:
            await svr.serve_forever()

    async def send_message(self, message):
        reader, writer = await asyncio.open_connection(self.mainip, 6767)
        writer.write(message.encode())
        data = await reader.read()
        message_in = json.loads(data.decode())
        print(message_in)
        message_start = message_in[0]
        if not message_start == "ok":
            print("Response error")
            print(message_in)
            exit()
        writer.close()

    async def receive_message(self, reader, writer):
        print("Message In")

        data = await reader.read()
        print(data)
        message = json.loads(data.decode())
        message_start = message[0]
        print("Received {0}".format(message))

        if message_start == "setup":
            message_out = json.dumps("ok")
            writer.write(message_out.encode())
            await self.send_message(json.dumps("ready"))
        elif message_start == "error":
            message_out = json.dumps("stop")
            writer.write(message_out.encode())
            exit()
        elif message_start == "stop":
            print("stopping")
            exit()
        elif message_start == "wait":
            message_out = json.dumps("ok")
            writer.write(message_out.encode())
            await self.send_message(json.dumps("waiting"))
        elif message_start == "test":
            print("Test successful")
        elif message_start == "capture":
            message_out = json.dumps("ok")
            writer.write(message_out.encode())
            results = self.detector.recognise(self.source.getImage())
            await self.send_message(json.dumps(("result", results)))


async def start_main():
    mn = Main('192.168.4.1', '192.168.4.14')
    asyncio.create_task(mn.open_server())


async def start_second():
    sc = Main('192.168.4.14', '192.168.4.1')
    asyncio.create_task(sc.open_server())
    await sc.send_message(json.dumps("start"))

# class Server:
#
#     def __init__(self, imagesource, detector):
#         self.secondaryResults = None
#         self.inputBlocker = asyncio.Event()
#         self.detector = detector
#         self.source = imagesource
#         self.exitKeyPressed = False
#
#     async def open_server(self):
#         svr = await asyncio.start_server(self.receive_message, "192.168.4.1", 6767)
#
#         async with svr:
#             await svr.serve_forever()
#
#     async def recognition_loop(self, writer: asyncio.StreamWriter):
#         while not self.exitKeyPressed:
#             self.inputBlocker.clear()
#             self.secondaryResults = None
#             writer.write(json.dumps("capture").encode())
#             localresults = self.detector.recognise(self.source.getImage())
#             await self.inputBlocker.wait()
#
#     async def receive_message(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
#         print("connected")
#         while True:
#             print("a")
#             while True:
#                 data = await reader.read(1)
#             print("b")
#             print(data)
#             message = json.loads(data.decode())
#             message_start = message[0]
#             logging.debug("Received {0}".format(message))
#             print("Received {0}".format(message))
#
#             if message_start == "start":
#                 message_out = json.dumps(("setup", self.detector.id()))
#                 writer.write(message_out.encode())
#             elif message_start == "error":
#                 logging.error("Received stop from client: {0}".format(message))
#                 message_out = json.dumps("stop")
#                 writer.write(message_out.encode())
#                 exit()
#             elif message_start == "result":
#                 message_out = json.dumps("wait")
#                 writer.write(message_out.encode())
#                 self.secondaryResults = message[1]
#             elif message_start == "ready":
#                 # Check if already exists sometime
#                 asyncio.create_task(self.recognition_loop(writer))
#             elif message_start == "test":
#                 print("Test successful")
#             else:
#                 # Throw exceptions here instead
#                 logging.error("Bad message returned: {0}, {1}".format(writer.get_extra_info("peername"), message))
#                 print("Bad message received, stopping")
#                 message_out = json.dumps("stop")
#                 writer.write(message_out.encode())
#                 exit()


# class Client:
#
#     def __init__(self, imagesource, detector):
#         self.detector = detector
#         self.source = imagesource
#         self.reader = None
#         self.writer = None
#         self.receive_task = None  # receive message loop
#
#     async def open_connection_test(self):
#         self.reader, self.writer = await asyncio.open_connection("192.168.4.1", 6767)
#
#         start_message = json.dumps("test")
#         self.writer.write(start_message.encode())
#
#         self.receive_task = asyncio.create_task(self.receive_message())
#
#     async def open_connection(self):
#         self.reader, self.writer = await asyncio.open_connection("192.168.4.1", 6767)
#
#         start_message = json.dumps("start")
#         self.writer.write(start_message.encode())
#
#         data = await self.reader.read()
#         msg = json.loads(data.decode())
#         if msg[0] == "setup":
#             await self.setup_detector(msg[1])
#             self.writer.write(json.dumps("ready").encode())
#         else:
#             logging.error("No setup message received: {0}".format(msg))
#         self.receive_task = asyncio.create_task(self.receive_message())
#
#     async def receive_message(self):
#         while True:
#             data = await self.reader.read()
#             msg = json.loads(data.decode())
#             message_start = msg[0]
#             logging.debug("Received {0}".format(msg))
#             print("Received {0}".format(msg))
#
#             if message_start == "capture":
#                 asyncio.create_task(self.capture())
#             elif message_start == "test":
#                 print("Test message received")
#                 message_out = json.dumps("test")
#                 self.writer.write(message_out.encode())
#
#     async def send_message(self, message):
#         # more logic some other time, separated so the receiver can get straight back to working
#         self.writer.write(message.encode())
#
#     async def capture(self):
#         results = self.detector.recognise(self.source.getImage())
#         message = json.dumps(("result", results))
#         await self.send_message(message)
#
#     async def setup_detector(self, detectorid):
#         # 1 = Full Cascade
#         # 2 = faster_rcnn_inception_resnet_v2_atrous_coco
#         # 3 = faster_rcnn_inception_v2_coco
#         # 4 = faster_rcnn_nas_coco
#         # 5 = faster_rcnn_resnet50_coco
#         # 6 = faster_rcnn_resnet101_coco
#         # 7 = rfcn_resnet101_coco
#         # 8 = ssd_inception_v2_coco
#         # 9 = ssd_mobilenet_v1_0.75_depth_300x300_coco14_sync
#         # 10 = ssd_mobilenet_v1_0.75_depth_quantized_300x300_coco14_sync
#         # 11 = ssd_mobilenet_v1_coco
#         # 12 = ssd_mobilenet_v1_quantized_300x300_coco14_sync
#         # 13 = ssd_mobilenet_v2_coco
#         # 14 = ssd_mobilenet_v2_quantized_300x300_coco
#         # 15 = ssdlite_mobilenet_v2_coco
#         if detectorid == "1":
#             import recognition.cascaderecognition
#             recog = recognition.cascaderecognition.server_cascade_setup()
#             self.detector = recog
#         elif detectorid == "2":
#             # TODO Tensorflow detect setup
#             exit()
