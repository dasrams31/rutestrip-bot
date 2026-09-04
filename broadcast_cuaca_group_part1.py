#!/usr/bin/env python3
import broadcast_cuaca_group

if __name__ == "__main__":
    p1 = broadcast_cuaca_group.fetch_weather_group(broadcast_cuaca_group.MOUNTAINS_PART1, "BAGIAN 1 - JATENG, DIY, & JABAR")
    print(p1)
