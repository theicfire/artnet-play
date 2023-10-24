This is a proof of concept to consume ArtNet on an ESP32, which then controls LEDs via FastLED.

# Arduino
Libraries required:
- ESP32 arduino library (includes WiFi.h, AsyncUDP.h)
- FastLED

## Programming steps
- We'll be using the Arduino IDE to program this for now
- Install the libraries
    - The ESP32 library is automatically installed when you install the ESP32 board in the board manager
    - Go to the libraries manager and search for FastLED
- Change the ssid/password in `arduino_main.cpp`
- Copy it to the IDE
- Choose your board and port
- Program!
- Watch the serial output. You should see it connect to wifi and give you the ip address.

# Hardware setup
- Plug the data pin of the LEDs (I tested with ws2812b) into D5. Ground into ground, power into VIN.

# Python
- `pip install pyartnet`
- You don't need to run `server.py`. That's just to check that `client.py` works.
- Change the ip address in `client.py` based on the serial output of the arduino
- Run `python client.py`
- You should see the first 3 leds breathing on and off every few seconds
- You can replace python with something like LXStudio
