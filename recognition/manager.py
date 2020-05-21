import asyncio
import json
from recognition.cascaderecognition import CascadeRecognition
import os
from recognition.picamerain import PiCameraInput


def server_cascade_setup():
    cascade_path = '/home/pi/FinalYearProject/camera/cas'
    scale = 1.4
    neighbours = 20
    size = '3030'
    recog = CascadeRecognition(scale, neighbours)
    for item in os.listdir(os.path.join(cascade_path, size)):
        recog.add_classifier(os.path.join(cascade_path, size, item, 'cascade.xml'), item)
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

        svr = await asyncio.start_server(self.receive_message, None, 8888)
        addr = svr.sockets[0].getsockname()
        print('Socket: {0}'.format(addr))

        async with svr:
            await svr.serve_forever()

    async def recognition_loop(self):
        print('rec')
        while not self.exitKeyPressed:
            self.secondaryResults = []
            await self.secondaryWaiting.wait()
            self.secondaryWaiting.clear()
            await self.send_message(json.dumps('capture'))
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
        print('Sending message: {0}'.format(message))
        reader, writer = await asyncio.open_connection(self.secondaryip, 8888)
        writer.write(message.encode())
        data = await reader.read()
        message_in = json.loads(data.decode())
        print(message_in)
        if isinstance(message_in, list):
            message_start = message_in[0]
        else:
            message_start = message_in
        if not message_start == 'ok':
            print('Response error')
            print(message_in)
            exit()
        writer.close()

    async def receive_message(self, reader, writer):
        print('Message In')

        data = await reader.read()
        print(data)
        message = json.loads(data.decode())
        if isinstance(message, list):
            message_start = message[0]
        else:
            message_start = message
        print('Received {0}'.format(message))
        print(message_start)

        if message_start == 'start':
            message_out = json.dumps('ok')
            writer.write(message_out.encode())
            writer.close()
            await self.send_message(json.dumps('setup'))
        elif message_start == 'error':
            message_out = json.dumps('stop')
            writer.write(message_out.encode())
            writer.close()
            exit()
        elif message_start == 'result':
            message_out = json.dumps('ok')
            writer.write(message_out.encode())
            writer.close()
            self.secondaryResults = message[1]
            self.secondaryComplete.set()
            await self.send_message(json.dumps('wait'))
        elif message_start == 'waiting':
            message_out = json.dumps('ok')
            writer.write(message_out.encode())
            writer.close()
            self.secondaryWaiting.set()
        elif message_start == 'ready':
            asyncio.create_task(self.recognition_loop())
        elif message_start == 'test':
            print('Test successful')
        elif message_start == 'stop':
            print('stopping')
            exit()
        else:
            print('Bad message received, stopping')
            message_out = json.dumps('stop')
            writer.write(message_out.encode())
            writer.close()
            exit()


class Secondary:
    def __init__(self, ip, mainip):
        self.waiting = asyncio.Event()
        self.detector = server_cascade_setup()  # Hard coded since TF isn't available
        self.source = PiCameraInput(768, 1024, 5, 30000)
        self.exitKeyPressed = False
        self.ip = ip
        self.mainip = mainip

    async def starter(self):
        await asyncio.sleep(10)
        await self.send_message(json.dumps('start'))

    async def open_server(self):
        svr = await asyncio.start_server(self.receive_message, None, 8888)
        asyncio.create_task(self.starter())
        addr = svr.sockets[0].getsockname()
        print('Socket: {0}'.format(addr))
        async with svr:
            await svr.serve_forever()

    async def send_message(self, message):
        print('Sending message: {0}'.format(message))
        reader, writer = await asyncio.open_connection(self.mainip, 8888)
        writer.write(message.encode())
        writer.write_eof()
        data = await reader.read()
        message_in = json.loads(data.decode())
        print(message_in)
        if isinstance(message_in, list):
            message_start = message_in[0]
        else:
            message_start = message_in
        if not message_start == 'ok':
            print('Response error')
            print(message_in)
            exit()
        writer.close()

    async def receive_message(self, reader, writer):
        print('Message In')

        data = await reader.read()
        print(data)
        message = json.loads(data.decode())
        if isinstance(message, list):
            message_start = message[0]
        else:
            message_start = message
        print('Received {0}'.format(message))

        if message_start == 'setup':
            message_out = json.dumps('ok')
            writer.write(message_out.encode())
            writer.close()
            await self.send_message(json.dumps('ready'))
        elif message_start == 'error':
            message_out = json.dumps('stop')
            writer.write(message_out.encode())
            writer.close()
            exit()
        elif message_start == 'stop':
            print('stopping')
            exit()
        elif message_start == 'wait':
            message_out = json.dumps('ok')
            writer.write(message_out.encode())
            writer.close()
            await self.send_message(json.dumps('waiting'))
        elif message_start == 'test':
            print('Test successful')
        elif message_start == 'capture':
            message_out = json.dumps('ok')
            writer.write(message_out.encode())
            writer.close()
            results = self.detector.recognise(self.source.getImage())
            await self.send_message(json.dumps(('result', results)))



async def start_main():
    mn = Main('192.168.4.1', '192.168.4.14')
    await mn.open_server()


async def start_second():
    sc = Secondary('192.168.4.14', '192.168.4.1')
    await sc.open_server()


async def test():
    reader, writer = await asyncio.open_connection('192.168.4.1', 8888)
    start_message = json.dumps('test')
    writer.write(start_message.encode())
    writer.close()

