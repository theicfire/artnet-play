
from stupidArtnet import StupidArtnet
import time
import random

# THESE ARE MOST LIKELY THE VALUES YOU WILL BE NEEDING
target_ip = '127.0.0.1'		# typically in 2.x or 10.x range
# target_ip = '192.168.2.2'
universe = 0 										# see docs
NUM_LEDS = 100
packet_size = NUM_LEDS * 3								# it is not necessary to send whole universe


def solid_color(r, g, b):
    channels = [r, g, b] * NUM_LEDS
    packet = bytearray(packet_size)
    for i in range(NUM_LEDS):
        packet[i*3] = channels[i*3]
        packet[i*3+1] = channels[i*3+1]
        packet[i*3+2] = channels[i*3+2]
    return packet


def set_color(r, g, b, universe):
    a.set_universe(universe)  # force sequence id to change, lol
    a.set(solid_color(r, g, b))						# only on changes
    a.show()							# send data


# CREATING A STUPID ARTNET OBJECT
# SETUP NEEDS A FEW ELEMENTS
# TARGET_IP   = DEFAULT 127.0.0.1
# UNIVERSE    = DEFAULT 0
# PACKET_SIZE = DEFAULT 512
# FRAME_RATE  = DEFAULT 30
# ISBROADCAST = DEFAULT FALSE
a = StupidArtnet(target_ip, universe, packet_size, 30, True, True)


colors = [
    [255, 0, 0],  # green
    [0, 255, 0],  # red
    [0, 0, 255]  # blue
]
a.sequence = 1
for i in range(1, 200):
    color = colors[i % len(colors)]
    print('set', color)
    set_color(color[0], color[1], color[2], 0)
    set_color(color[0], color[1], color[2], 1)
    time.sleep(1 / 100.0)

# set_color(255, 0, 0)
# time.sleep(.5)
# set_color(0, 255, 0)
