import asyncio
import json
from recognition.cascaderecognition import CascadeRecognition
import os
from recognition.picamerain import PiCameraInput
import numpy as np


def server_cascade_setup():
    cascade_path = '/home/pi/FinalYearProject/camera/cas'
    scale = 1.4
    neighbours = 20
    size = '3030'
    recog = CascadeRecognition(scale, neighbours)
    for item in os.listdir(os.path.join(cascade_path, size)):
        print(os.path.join(cascade_path, size, item, "cascade.xml"))
        recog.add_classifier(os.path.join(cascade_path, size, item, "cascade.xml"), item)
    recog.toggle_clean(True)
    recog.load_test()
    return recog


def best_bounding_box(match):
    high_pos_loc = 0
    if len(match[1][2]) >= 1:
        for strengthposition, strengthvalue in enumerate(match[1][2]):
            if strengthvalue >= match[1][2][strengthposition]:
                high_pos_loc = strengthposition
        ret_val = [match[0], [match[1][0][high_pos_loc], [], match[1][2][high_pos_loc]]]
        return ret_val
    elif len(match[1][2]) == 0:
        return None
    else:
        return match


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
            print("awaiting waiting")
            await self.secondaryWaiting.wait()
            self.secondaryWaiting.clear()
            await self.send_message(json.dumps('capture'))
            localresults = self.detector.recognise(self.source.getImage())
            print("awaiting complete")
            await self.secondaryComplete.wait()
            self.secondaryComplete.clear()
            final_matches = []
            # Visual layout of the value matches is in the report appendix
            # All classifiers always return, even if its all empty
            for counter, item in enumerate(localresults):  # 0
                local_best = best_bounding_box(item)
                secondary_best = best_bounding_box(self.secondaryResults[counter])
                if local_best is None and secondary_best is None:
                    continue
                elif local_best is None and secondary_best is not None:
                    final_matches.append(secondary_best)
                elif secondary_best is None and local_best is not None:
                    final_matches.append(local_best)
                elif local_best is not None and secondary_best is not None:
                    if local_best[1][2] >= secondary_best[1][2]:
                        final_matches.append(local_best)
                    else:
                        final_matches.append(secondary_best)
            if len(final_matches) >= 1:
                print(final_matches)
            else:
                print("No matches")


    async def send_message(self, message):
        print('Sending message: {0}'.format(message))
        reader, writer = await asyncio.open_connection(self.secondaryip, 8888)
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
            await self.send_message(json.dumps('wait'))
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
        await asyncio.sleep(2)
        await self.send_message(json.dumps('start'))

    async def open_server(self):
        svr = await asyncio.start_server(self.receive_message, None, 8888)
        addr = svr.sockets[0].getsockname()
        print('Socket: {0}'.format(addr))
        async with svr:
            await asyncio.gather(self.starter(), svr.serve_forever())

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

