import sys
import json
from datetime import datetime, timedelta

ITINERARY_DATA = {
    "sumbing": {
        "name": "Gunung Sumbing (via Kaliangkrik)",
        "pos": [
            {"name": "Basecamp (Nepal van Java)", "dist_km": 0.0, "ele": 1726},
            {"name": "Pos 1 (Griya Satwa)", "dist_km": 1.5, "ele": 2000},
            {"name": "Pos 2 (Syahadat)", "dist_km": 3.0, "ele": 2400},
            {"name": "Pos 3 (Camp Area)", "dist_km": 4.5, "ele": 2750},
            {"name": "Pos 4 (Dinding Hari)", "dist_km": 5.2, "ele": 3050},
            {"name": "Puncak Sejati", "dist_km": 5.9, "ele": 3341}
        ]
    },
    "merbabu": {
        "name": "Gunung Merbabu (via Selo)",
        "pos": [
            {"name": "Basecamp Selo", "dist_km": 0.0, "ele": 1800},
            {"name": "Pos 1 (Dokarian)", "dist_km": 1.8, "ele": 2150},
            {"name": "Pos 2 (Selokenang)", "dist_km": 3.2, "ele": 2400},
            {"name": "Pos 3 (Batu Tulis - Camp)", "dist_km": 4.5, "ele": 2600},
            {"name": "Pos 4 (Sabana 1)", "dist_km": 5.5, "ele": 2850},
            {"name": "Pos 5 (Sabana 2)", "dist_km": 6.2, "ele": 2980},
            {"name": "Puncak Kenteng Songo", "dist_km": 6.7, "ele": 3145}
        ]
    }
}

def naismith_hours(d_km, gain_m):
    return (d_km / 5.0) + (gain_m / 600.0)

def generate_itinerary(mountain_key="sumbing", mode="2d1n", start_time="07:00"):
    key = mountain_key.lower()
    data = ITINERARY_DATA.get(key, ITINERARY_DATA["sumbing"])
    pos_list = data["pos"]
    
    t_fmt = "%H:%M"
    curr_t = datetime.strptime(start_time, t_fmt)
    
    timeline = []
    timeline.append(f"⏱️ **ITINERARY PENDAKIAN: {data['name']} ({mode.upper()})**")
    timeline.append(f"🚀 Start Basecamp: {curr_t.strftime(t_fmt)}")
    timeline.append("-" * 40)
    
    for i in range(1, len(pos_list)):
        prev = pos_list[i-1]
        curr = pos_list[i]
        d = curr["dist_km"] - prev["dist_km"]
        gain = max(0, curr["ele"] - prev["ele"])
        hrs = naismith_hours(d, gain)
        mins = int(hrs * 60)
        curr_t += timedelta(minutes=mins)
        timeline.append(f"• {prev['name']} ➔ {curr['name']}: ~{mins} mnt | Arrive: **{curr_t.strftime(t_fmt)}**")
        
        if mode == "2d1n" and "Camp" in curr["name"]:
            timeline.append(f"  ⛺ *CAMP & ISTIRAHAT DARI {curr_t.strftime(t_fmt)}*")
            curr_t = datetime.strptime("03:30", t_fmt) # Summit attack time
            timeline.append(f"  🌄 *SUMMIT ATTACK BESOK JAM {curr_t.strftime(t_fmt)}*")
            
    return "\n".join(timeline)

def generate_logistics(group_size=3, days=2):
    water_l = group_size * days * 3.0
    gas_canisters = round(group_size * days * 0.75)
    tents = (group_size + 3) // 4
    
    out = [
        f"🎒 **LOGISTIK & GEAR CHECKLIST ({group_size} Orang, {days} Hari)**",
        f"• 💧 **Air Bersih:** {water_l:.1f} Liter total ({days*3}L / orang)",
        f"• ⛺ **Tenda Dome:** {tents} unit (Kapasitas 4)",
        f"• ⛽ **Gas Kaleng:** {gas_canisters} kaleng + 1 kompor portable",
        f"• 🍲 **Logistik Makanan:** {group_size * days * 3} porsi utama + snack energi",
        f"• 🧥 **Personal Gear (Wajib):** Jaket gunung, sleeping bag, matras, headlamp, raincoat, sepatu trekking",
        f"• 🚑 **Safety & Medical:** P3K (obat pribadi, oxycan, thermal blanket, povidone), Trash bag x{group_size}"
    ]
    return "\n".join(out)

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "all"
    if action == "itinerary":
        m = sys.argv[2] if len(sys.argv) > 2 else "sumbing"
        mode = sys.argv[3] if len(sys.argv) > 3 else "2d1n"
        print(generate_itinerary(m, mode))
    elif action == "logistics":
        people = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 2
        print(generate_logistics(people, days))
    else:
        print(generate_itinerary())
        print("\n" + generate_logistics())
