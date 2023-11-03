#!/bin/bash

# IP address you want to check connectivity with
IP_ADDRESS="192.168.1.156"

# Infinite loop to keep trying until we can ping the IP address
while true; do
    echo 'loop'
    if ping -c 1 -t 1 "$IP_ADDRESS" &> /dev/null; then
        # If ping is successful, make a sound and speak a message, then exit
        echo "Ping successful"
        say "Ping successful"
        exit 0
    else
        echo 'waiting..'
        # Wait for a second before trying again
        sleep 1
    fi
done

