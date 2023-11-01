import time
import asyncio
import json
from collections import namedtuple
import base64
from chase_types import ArtNetData

ART_NET_PORT = 6454
ART_NET_HEADER = b'Art-Net\x00'


class ArtNetRecorder(asyncio.DatagramProtocol):
    data_list = []
    recording = True
    start_time = None

    def __init__(self):
        self.transport = None

    def add_data(self, data):
        if not self.start_time:
            self.start_time = time.time()
        ms = (time.time() - self.start_time) * 1000
        self.data_list.append(ArtNetData(ms, data))

    def datagram_received(self, data, addr):
        # print('data', data)
        if data.startswith(ART_NET_HEADER):
            opcode = data[8:10]
            if opcode == b'\x00P':
                universe = data[14] + 256 * data[15]
                dmx_data = data[18:]
                has_data = any(dmx_data)
                print(
                    f"Received Art-Net data from {addr[0]}:{addr[1]} for Universe {universe}, has_data: {has_data}")
                self.add_data(data)

    async def receive_artnet_data(self):
        loop = asyncio.get_running_loop()
        self.transport, _ = await loop.create_datagram_endpoint(
            lambda: self, local_addr=('0.0.0.0', ART_NET_PORT)
        )
        print(f"Listening for Art-Net data on port {ART_NET_PORT}...")

        while self.recording:
            await asyncio.sleep(1)  # Just to keep the task alive

    async def wait_for_stop_command(self):
        while self.recording:
            user_input = await asyncio.to_thread(input, "Press 's' to stop recording: ")
            if user_input == 's':
                self.recording = False
                if self.transport:
                    self.transport.close()

    def save_to_json(self):
        with open('artnet_data.json', 'w') as f:
            json_data = [{
                'time': entry.time,
                'data': base64.b64encode(entry.data).decode('utf-8')
            } for entry in self.data_list]
            json.dump(json_data, f)


async def main():
    recorder = ArtNetRecorder()
    tasks = asyncio.gather(recorder.receive_artnet_data(),
                           recorder.wait_for_stop_command())
    await tasks
    recorder.save_to_json()

if __name__ == "__main__":
    asyncio.run(main())
