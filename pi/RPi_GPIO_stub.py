# Constants
BCM = 'BCM'
BOARD = 'BOARD'
OUT = 'OUT'
IN = 'IN'
PUD_OFF = 'PUD_OFF'
PUD_DOWN = 'PUD_DOWN'
PUD_UP = 'PUD_UP'
HIGH = True
LOW = False
RISING = 'RISING'
FALLING = 'FALLING'
BOTH = 'BOTH'

# Setup methods


def setmode(mode):
    pass


def setwarnings(flag):
    pass


def setup(channel, state, pull_up_down=PUD_OFF, initial=LOW):
    pass


def cleanup(channel=None):
    pass

# Input and Output methods


def input(channel):
    return False


def output(channel, state):
    pass

# Event methods


def add_event_detect(channel, edge, callback=None, bouncetime=None):
    pass


def remove_event_detect(channel):
    pass


def event_detected(channel):
    return False


def add_event_callback(channel, callback):
    pass


def wait_for_edge(channel, edge, timeout=None):
    pass

# PWM class stub


class PWM:
    def __init__(self, channel, frequency):
        self.channel = channel
        self.frequency = frequency
        self.start_val = 0

    def start(self, duty_cycle):
        self.start_val = duty_cycle
        pass

    def ChangeDutyCycle(self, duty_cycle):
        pass

    def ChangeFrequency(self, frequency):
        pass

    def stop(self):
        pass
