import asyncio
from pyartnet import ArtNetNode


async def breathe_led(universe, color):
    # Add a channel for the LED in the given universe
    print('colors len', len(color))
    channel = universe.add_channel(start=1, width=len(color))

    # while True:
    print('fade in..')
    # Fade in
    channel.add_fade(color, 2000)
    await channel  # Wait for the fade in to complete

    print('fade out..')
    # Fade out
    channel.add_fade([0, 0, 0] * (len(color) // 3), 2000)
    await channel  # Wait for the fade out to complete


class StripHolder:
    led_channels = []

    def add_strip(self, channels):
        self.led_channels = self.led_channels + channels

    def get_universes(self):
        ret = []
        for i in range(0, len(self.led_channels), 510):
            ret.append(self.led_channels[i:i + 510])
        return ret


async def main():
    # node = ArtNetNode('192.168.1.139', 6454)
    # node = ArtNetNode('192.168.1.174', 6454)
    node = ArtNetNode('127.0.0.1', 6454)

    holder = StripHolder()
    holder.add_strip([200, 0, 0] * 170)
    holder.add_strip([0, 200, 0] * 170)
    # holder.add_strip([0, 0, 200] * 85)
    # holder.add_strip([200, 0, 200] * 85)
    # holder.add_strip([0, 200, 200] * 85)
    # holder.add_strip([200, 200, 0] * 85)

    colors = holder.get_universes()

    # Create universes and start LED breathing tasks
    tasks = []
    for i in range(len(colors)):
        print('universe', i)
        universe = node.add_universe(i)
        tasks.append(breathe_led(universe, colors[i]))

    # Use asyncio.gather to run all LED breathing functions concurrently
    await asyncio.gather(*tasks)

asyncio.run(main())
