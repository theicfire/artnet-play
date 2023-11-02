import json
import base64
import time
from collections import namedtuple
import socket
from chase_types import ArtNetData

# TARGET_IP = "127.0.0.1"
TARGET_IP = "192.168.2.2"
TARGET_PORT = 6454


class ArtNetPlayer():
    data_list = []
    sock = None

    def __init__(self):
        with open('artnet_data.json', 'r') as f:
            json_data = json.load(f)
            self.data_list = [ArtNetData(entry['time'], base64.b64decode(
                entry['data'])) for entry in json_data]

        # TODO sock.close() later?
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def play(self):
        start_time = time.time()
        i = 0
        while i < len(self.data_list) - 1:
            entry = self.data_list[i]
            ms = (time.time() - start_time) * 1000

            if ms < entry.time:
                print('sleep', entry.time - ms)
                time.sleep((entry.time - ms) / 1000.0)
                continue

            selected_entry = entry
            i += 1
            if self.sock:
                print('play out', selected_entry.time, selected_entry.data[14])
                self.sock.sendto(selected_entry.data, (TARGET_IP, TARGET_PORT))

        print('Done playing')


if __name__ == "__main__":
    player = ArtNetPlayer()
    player.play()
