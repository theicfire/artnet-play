import traceback
import simpleaudio as sa
import sys
from pathlib import Path
import asyncio
import socket
import time
import base64
import json

if sys.platform == 'linux' or sys.platform == 'linux2':
    import RPi.GPIO as GPIO
else:
    import RPi_GPIO_stub as GPIO

current_dir = Path(__file__).parent
# recorder_package_path = (current_dir / "../recorder").resolve()
project_root = (current_dir / "..").resolve()
sys.path.append(str(project_root))
# sys.path.append(str(recorder_package_path))

from recorder.recorder_types import ArtNetData  # noqa

# TARGET_IP = "127.0.0.1"
# TARGET_IP = "192.168.2.2"
TARGET_PORT = 6454
TARGET_IP = "192.168.1.148"  # wifi
if sys.platform == 'linux' or sys.platform == 'linux2':
    TARGET_IP = "10.42.0.2"  # ethernet


class ArtNetPlayer():

    def __init__(self):
        # TODO sock.close() later?
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.sock.setblocking(False)
        # self.loop = asyncio.get_event_loop()
        self.running = False

    def fade_out(self, universe_last_played):
        # TODO better brightness curve
        FPS = 60
        FADE_TIME__ms = 1000
        NUM_STEPS = int(FPS * FADE_TIME__ms / 1000.0)
        for i in range(NUM_STEPS + 1):
            for _, raw_data in universe_last_played.items():
                data = bytearray(raw_data)
                for j in range(18, len(data)):
                    data[j] = int(data[j] * (NUM_STEPS - i) / NUM_STEPS)
                if self.sock:
                    self.sock.sendto(data, (TARGET_IP, TARGET_PORT))
            time.sleep(1.0 / FPS)
        time.sleep(1)

    async def play(self, file_name, loop=False):
        file_name = str(
            (Path(__file__).parent.parent / "recorder" / file_name))

        self.running = True
        data_list = []
        last_played = {}  # universe -> data
        with open(file_name, 'r') as f:
            json_data = json.load(f)
            data_list = [ArtNetData(entry['time'], base64.b64decode(
                entry['data'])) for entry in json_data]
        start_time = time.time()
        i = 0
        if loop:
            print('Play background sequence')
        else:
            print('Play main sequence')
        while self.running:
            entry = data_list[i]
            ms = (time.time() - start_time) * 1000

            if ms < entry.time:
                await asyncio.sleep((entry.time - ms) / 1000.0)
                continue

            selected_entry = entry
            i += 1
            if i >= len(data_list):
                if loop:
                    i = 0
                    start_time = time.time()
                else:
                    self.running = False

            if self.sock:
                universe = selected_entry.data[14]
                # print('play out', selected_entry.time, universe)
                # TODO make async with loop.sock_sendto .. python 3.11
                self.sock.sendto(selected_entry.data,
                                 (TARGET_IP, TARGET_PORT))
                last_played[universe] = selected_entry.data
            else:
                print('Cannot find socket, quitting..')
                sys.exit(1)

        if loop:
            print('Fade out')
            self.fade_out(last_played)
            print('Done playing background sequence')
        else:
            print('Done playing main sequence')

    def stop(self):
        self.running = False

    def close(self):
        self.running = False
        if self.sock:
            self.sock.close()
            self.sock = None


def handle_task_result(task):
    try:
        # This will re-raise any exception that was raised in the task.
        task.result()
    except Exception as e:
        print(f"An error occurred in play_background: {e}")
        traceback.print_exc()  # This will print the stack trace.
        sys.exit(1)  # Exit the program.


def play_background(player):
    task = asyncio.create_task(player.play('artnet_data.json', loop=True))
    task.add_done_callback(handle_task_result)
    return task


def clear_event_detect(pin):
    # Read and ignore
    GPIO.event_detected(pin)


async def main():
    player = ArtNetPlayer()
    audio_fname = str(Path(__file__).with_name("arcade.wav"))
    wave_obj = sa.WaveObject.from_wave_file(audio_fname)

    play_task = play_background(player)

    PIN = 3  # AKA GPIO2
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PIN, GPIO.IN)
    GPIO.add_event_detect(PIN, GPIO.FALLING)

    while True:
        await asyncio.sleep(0.1)
        if GPIO.event_detected(PIN):
            print("Pin fell! Now read: ", GPIO.event_detected(PIN))
            player.stop()

            play_obj = wave_obj.play()
            await play_task
            await player.play('artnet_data.json')
            play_obj.wait_done()  # Should be immediate
            play_task = play_background(player)
            clear_event_detect(PIN)
    # GPIO.cleanup()


asyncio.run(main())
