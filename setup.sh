set -e
#!/bin/bash

# Check if the script is running as root
if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root." >&2
  exit 1
fi

sudo apt update

# Really should exist by default.. https://github.com/raspberrypi/bookworm-feedback/issues/90
sudo apt install python3.11-venv

# TODO make requirements.txt
/home/pi/artnet-play/venv/bin/pip install simpleaudio
/home/pi/artnet-play/venv/bin/pip  install RPi.GPIO

# Run if venv doesn't exist

if [ ! -d "venv" ]; then
  echo "venv doesn't exist, creating..."
  python3 -m venv venv
fi

# Define the service file path
PLAY_SERVICE_FILE=run_play.service
cp $PLAY_SERVICE_FILE /etc/systemd/system/
systemctl daemon-reload
systemctl enable $PLAY_SERVICE_FILE
systemctl restart $PLAY_SERVICE_FILE
echo "Service '$PLAY_SERVICE_FILE' has been installed, enabled, and started."

WIFI_SERVICE_FILE=disable_wifi_power_save.service
cp $WIFI_SERVICE_FILE /etc/systemd/system/
systemctl daemon-reload
systemctl enable $WIFI_SERVICE_FILE
systemctl restart $WIFI_SERVICE_FILE
echo "Service '$WIFI_SERVICE_FILE' has been installed, enabled, and started."
