#!/usr/bin/env python3
import sys
import os
sys.path.append("/home/ubuntu/rutestrip-bot")
import broadcast_cuaca_group
from telegram_broadcast_helper import broadcast_to_subscribers

if __name__ == "__main__":
    p2 = broadcast_cuaca_group.fetch_weather_group(broadcast_cuaca_group.MOUNTAINS_PART2, "BAGIAN 2 - JABAR, JATIM, & BALI")
    if "--no-send" not in sys.argv:
        broadcast_to_subscribers(p2, targets="channel")
    print(p2)
