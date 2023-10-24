#include <WiFi.h>
#include <FastLED.h>
#include <AsyncUDP.h>

// WiFi settings
const char* ssid = "xx";
const char* password = "xx";
// Art-Net settings
const int ART_NET_PORT = 6454;
const int START_UNIVERSE = 0;  // starting from 0

// LED strip settings
#define NUM_LEDS 3  // Number of LEDs in the strip
#define DATA_PIN 5    // Connect the data pin of the WS2812B to this pin on ESP32

CRGB leds[NUM_LEDS];
AsyncUDP udp;

void setup() {
    // Start the serial communication
    Serial.begin(115200);

    // Connect to Wi-Fi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");

    // Start FastLED with the settings
    FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);

    // Listen for UDP packets
    if (udp.listen(ART_NET_PORT)) {
        Serial.println("UDP Listening on IP: " + WiFi.localIP().toString());
        
        // Define the packet handling function
        udp.onPacket([](AsyncUDPPacket& packet) {
            Serial.printf("Got msg. First byte %d, len: %d\n", packet.data()[0], packet.length());
            if (packet.length() > 10) {
              Serial.printf("%d %d %d %d %d %d %d %d\n", packet.data()[0], packet.data()[1], packet.data()[2], packet.data()[3], packet.data()[4], packet.data()[5], packet.data()[6], packet.data()[7]);
                // Check if it's an Art-Net packet
                if (packet.data()[0] == 'A' && packet.data()[1] == 'r' && packet.data()[2] == 't' && packet.data()[3] == '-') {
                    uint16_t universe = packet.data()[14] | (packet.data()[15] << 8);  // little endian
                    if (universe == START_UNIVERSE) {
                        int channelDataStart = 18;
                        for (int i = 0; i < NUM_LEDS; i++) {
                            // Each LED needs 3 channels: R, G, and B
                            leds[i].r = packet.data()[channelDataStart + i * 3];
                            leds[i].g = packet.data()[channelDataStart + i * 3 + 1];
                            leds[i].b = packet.data()[channelDataStart + i * 3 + 2];
                        }
                        FastLED.show();
                    }
                }
            }
        });
    }
}

void loop() {
    // Do nothing here.
}
