#!/bin/bash

# Check if the script is running as root
if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root." >&2
  exit 1
fi

# Define the service file path
SERVICE_FILE=run_play.service

cp $SERVICE_FILE /etc/systemd/system/

systemctl daemon-reload
systemctl enable $SERVICE_FILE
systemctl restart $SERVICE_FILE
echo "Service '$SERVICE_FILE' has been installed, enabled, and started."
