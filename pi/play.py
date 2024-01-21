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
project_root = (current_dir / "..").resolve()
sys.path.append(str(project_root))

from recorder.recorder_types import ArtNetData  # noqa

TARGET_PORT = 6454
# TARGET_IP = "192.168.1.148"  # wifi, for local development
ch_to_ip = {
    0: "192.168.1.148",
    1: "192.168.1.148",
    2: "192.168.1.148",
    3: "192.168.1.148",
    4: "192.168.1.148",
    5: "192.168.1.148",
    6: "192.168.1.148",
    7: "192.168.1.148",
    8: "192.168.1.148",
    9: "192.168.1.148",
    10: "192.168.1.148",
    11: "192.168.1.148",
    12: "192.168.1.148",
}

if sys.platform == 'linux' or sys.platform == 'linux2':
    ch_to_ip = {
        0: "10.42.0.2",
        1: "10.42.0.2",
        2: "10.42.0.2",
        3: "10.42.0.2",
        4: "10.42.0.2",
        5: "10.42.0.2",
        6: "10.42.0.2",
        7: "10.42.0.2",
        8: "10.42.0.3",
        9: "10.42.0.3",
        10: "10.42.0.3",
        11: "10.42.0.3",
        12: "10.42.0.3",
        13: "10.42.0.3",
        14: "10.42.0.3",
        15: "10.42.0.3",
        16: "10.42.0.3",
        17: "10.42.0.3",
        18: "10.42.0.3",
    }

BACKGROUND_SEQUENCE_FNAME = 'background_sequence.json'
MAIN_SEQUENCE_FNAME = 'main_sequence.json'
AUDIO_FNAME = 'ascension.wav'


class ArtNetPlayer():

    def __init__(self):
        # TODO sock.close() later?
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Crazy RPI issue. If sending to > 1 ip address and something can't be resolved, sendto will hang :(. So instead just try/catch and don't block.
        self.sock.setblocking(False)
        # self.loop = asyncio.get_event_loop()
        self.running = False
        file_name = str(
            (Path(__file__).parent.parent / "recorder" / MAIN_SEQUENCE_FNAME))
        with open(file_name, 'r') as f:
            json_data = json.load(f)
            self.main_sequence = [ArtNetData(entry['time'], base64.b64decode(
                entry['data'])) for entry in json_data]

        file_name = str(
            (Path(__file__).parent.parent / "recorder" / BACKGROUND_SEQUENCE_FNAME))
        with open(file_name, 'r') as f:
            json_data = json.load(f)
            self.background_sequence = [ArtNetData(entry['time'], base64.b64decode(
                entry['data'])) for entry in json_data]

    def fade_out(self, universe_last_played):
        # TODO better brightness curve
        FPS = 60
        FADE_TIME__ms = 250
        NUM_STEPS = int(FPS * FADE_TIME__ms / 1000.0)
        for i in range(NUM_STEPS + 1):
            for universe, raw_data in universe_last_played.items():
                data = bytearray(raw_data)
                for j in range(18, len(data)):
                    data[j] = int(data[j] * (NUM_STEPS - i) / NUM_STEPS)
                if self.sock:
                    self.sock.sendto(data, (ch_to_ip[universe], TARGET_PORT))
            time.sleep(1.0 / FPS)
        # time.sleep(0.5)

    async def play(self, is_main):

        loop = not is_main
        self.running = True
        data_list = []
        last_played = {}  # universe -> data
        data_list = self.main_sequence if is_main else self.background_sequence
        start_time = time.time()
        i = 0
        if is_main:
            print('Play main LED sequence')
        else:
            print('Play background LED sequence')
        exception_count = 0
        while self.running:
            entry = data_list[i]
            ms = (time.time() - start_time) * 1000

            if ms < entry.time:
                if (entry.time - ms) > 1000:
                    print('Error, would have waited too long: ', (entry.time - ms))
                else:
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
                try:
                    # TODO make async with loop.sock_sendto .. python 3.11
                    self.sock.sendto(selected_entry.data,
                                     (ch_to_ip[universe], TARGET_PORT))
                except Exception as e:
                    if exception_count % 100 == 0:
                        print(f"Sendto err: {e}")
                        # traceback.print_exc()
                    exception_count += 1
                last_played[universe] = selected_entry.data
            else:
                print('Cannot find socket, quitting..')
                sys.exit(1)

        if is_main:
            print('Done playing main sequence')
        else:
            print('Fade out')
            self.fade_out(last_played)
            print('Done playing background sequence')

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
        print(f"An error occurred in handle_task_result: {e}")
        traceback.print_exc()  # This will print the stack trace.
        sys.exit(1)  # Exit the program.


def play_background(player):
    task = asyncio.create_task(player.play(
        is_main=False))
    task.add_done_callback(handle_task_result)
    return task


def play_main(player):
    task = asyncio.create_task(player.play(
        is_main=True))
    task.add_done_callback(handle_task_result)
    return task


async def main():
    player = ArtNetPlayer()
    audio_fname = str(Path(__file__).with_name(AUDIO_FNAME))
    wave_obj = sa.WaveObject.from_wave_file(audio_fname)

    play_task = play_background(player)

    PIN = 3  # AKA GPIO2
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PIN, GPIO.IN)
    GPIO.add_event_detect(PIN, GPIO.FALLING)

    play_obj = None

    async def reset_to_background():
        nonlocal play_task
        nonlocal play_obj
        player.stop()
        await play_task
        play_task = play_background(player)
        play_obj.stop()
        play_obj = None

    ascend_print__s = time.time()
    while True:
        await asyncio.sleep(0.1)
        if GPIO.event_detected(PIN):
            if play_obj == None:
                print("Pin fell! Now read: ", GPIO.event_detected(PIN))
                play_obj = wave_obj.play()

                player.stop()
                await play_task
                print("Now play main")
                play_task = play_main(player)
            else:
                print('Pin fell. Cancelling because we are already playing')
                await reset_to_background()
        ascension_running = play_obj != None
        if ascension_running:
            ascension_finished = not player.running and not play_obj.is_playing()
            if ascension_finished:
                print('Finished ascension')
                await reset_to_background()
            elif time.time() - ascend_print__s > .5:
                print('Ascension running..')
                ascend_print__s = time.time()

    # GPIO.cleanup()


asyncio.run(main())
