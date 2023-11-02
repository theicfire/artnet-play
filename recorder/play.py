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
    sock = None

    def __init__(self):
        # TODO sock.close() later?
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def play(self, file_name):
        data_list = []
        with open(file_name, 'r') as f:
            json_data = json.load(f)
            data_list = [ArtNetData(entry['time'], base64.b64decode(
                entry['data'])) for entry in json_data]
        start_time = time.time()
        i = 0
        while i < len(data_list) - 1:
            entry = data_list[i]
            ms = (time.time() - start_time) * 1000

            if ms < entry.time:
                time.sleep((entry.time - ms) / 1000.0)
                continue

            selected_entry = entry
            i += 1
            if self.sock:
                universe = selected_entry.data[14]
                print('play out', selected_entry.time, universe)
                self.sock.sendto(selected_entry.data, (TARGET_IP, TARGET_PORT))

        print('Done playing')


if __name__ == "__main__":
    player = ArtNetPlayer()
    player.play('artnet_data.json')
