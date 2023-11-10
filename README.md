Take a look at the main repo for LXStudio, keypad ESP code, and MIDI controller stuff: https://github.com/cstigler/LXStudio-AscensionPod/tree/master

This repo does a few things:

1. Records artnet data to a file
2. Sets up and runs a python program on a Raspberry Pi that plays these recordings, and also plays audio
3. There's some half-working demo code of the ESP32 reading ArtNet and controlling LED strips. We changed paths and instead purchased a [pre-built LED controller](https://chroma.tech/) to speed things up. Note that the pre-built controller is also an ESP32, so this is still a viable option.

# Recording ArtNet

- python recorder/record.py
- Send ArtNet data to 127.0.0.1:6454 (default ArtNet port)
- Press 's' + Enter to stop recording and save the file
- Move the file to `recorder/main_sequence.json` or `recorder/background.java` (Save as `MAIN_SEQUENCE_FNAME`, `BACKGROUND_FNAME`)

# Pi

## Setup

- Install the RPI image to the sd card via the Raspberry Pi Imager program. Change the settings such that ssh is turned on, and there's a default user
- Turn on the RPI with the imaged sd card
- "share ethernet" from mac. Connect mac ethernet to RPI.
- ssh pi@pi.local
- sudo raspi-config nonint do_wifi_ssid_passphrase "spacebase2" meowmeow2
  - I don't know why the RPI imager wifi settings didn't work automatically for me.
- Get the wifi ip address
- Now ssh via wifi
- sudo apt update
- mkdir -p artnet-play
- Make the RPI act as a router, so that it can give the LED controller an ip address and communicate with it.
  - sudo nmcli c add con-name pi-eth-shared type ethernet ifname eth0 ipv4.method shared ipv6.method ignore
  - sudo nmcli c up pi-eth-shared
- Add ssh keys for convenience
  - This could alternatively be done via the Imager program
  - mkdir -p ~/.ssh
  - vim ~/.ssh/authorized_keys
    - add key..
- Now upload all these files on by running this locally:
  - rsync -avz ../artnet-play  pi@192.168.1.156:~/
- Then run this on the RPI:
  - `cd ~/artnet-play/pi && sudo sh setup_pi.sh`

play.py should be running now, and will run at startup. Note the following:

- `BACKGROUND_SEQUENCE_FNAME`
- `MAIN_SEQUENCE_FNAME`
- `AUDIO_FNAME`

## Get Logs

- `journalctl -u run_play.service -f`

