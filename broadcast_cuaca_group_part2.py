#!/usr/bin/env python3
import broadcast_cuaca_group

if __name__ == "__main__":
    p2 = broadcast_cuaca_group.fetch_weather_group(broadcast_cuaca_group.MOUNTAINS_PART2, "BAGIAN 2 - JABAR, JATIM, & BALI")
    print(p2)
