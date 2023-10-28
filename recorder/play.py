import json
import base64
import time
from collections import namedtuple
import socket
from chase_types import ArtNetData

TARGET_IP = "127.0.0.1"
TARGET_PORT = 6454


class ArtNetPlayer():
    data_list = []
    sock = None

    def __init__(self):
        # read json file
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
            next_entry = self.data_list[i+1]
            ms = (time.time() - start_time) * 1000
            if ms >= next_entry.time:
                i += 1
                continue

            selected_entry = None
            if ms - entry.time < next_entry.time - ms:
                selected_entry = entry
                i += 1
            else:
                selected_entry = next_entry
                i += 2
            if self.sock:
                print('play out', selected_entry.time)
                self.sock.sendto(selected_entry.data, (TARGET_IP, TARGET_PORT))

            time.sleep(1 / 60.0)
        print('Done playing')


if __name__ == "__main__":
    player = ArtNetPlayer()
    player.play()
