#!/usr/bin/env python3
import broadcast_cuaca_group
from telegram_broadcast_helper import broadcast_to_subscribers

if __name__ == "__main__":
    p1 = broadcast_cuaca_group.fetch_weather_group(broadcast_cuaca_group.MOUNTAINS_PART1, "BAGIAN 1 - JATENG, DIY, & JABAR")
    # Kirim ke seluruh grup Telegram
    broadcast_to_subscribers(p1, targets="groups")
    # Cetak agar Admin juga menerima hasil cron
    print(p1)
