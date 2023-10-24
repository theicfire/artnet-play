import asyncio
from pyartnet import ArtNetNode

async def main():
    node = ArtNetNode('192.168.1.139', 6454)

    # Create universe 0
    universe = node.add_universe(0)

    # Add a channel to the universe which consists of 3 values
    channel = universe.add_channel(start=1, width=9)

    while True:
        # Fade in
        channel.add_fade([255, 0, 0, 0, 255, 0, 0, 0, 255], 2000)
        await channel  # Wait for the fade in to complete

        # Fade out
        channel.add_fade([0, 0, 0, 0, 0, 0, 0, 0, 0], 2000)
        await channel  # Wait for the fade out to complete

asyncio.run(main())
