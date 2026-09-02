import sys
import json

CONTACTS_DB = {
    "sumbing": {
        "name": "Gunung Sumbing",
        "basecamps": [
            {"jalur": "Nepal van Java (Butuh Kaliangkrik)", "basecamp_tel": "+6281234567801", "ojek": "Rp 30.000 / trip (Basecamp ➔ Pos 1)", "porter": "Rp 300.000 - Rp 400.000 / hari (beban maks 20kg)"},
            {"jalur": "Garung (Kledung)", "basecamp_tel": "+6281234567802", "ojek": "Rp 25.000 / trip", "porter": "Rp 350.000 / hari"},
            {"jalur": "Bowongso", "basecamp_tel": "+6281234567803", "ojek": "Rp 20.000 / trip", "porter": "Rp 300.000 / hari"}
        ]
    },
    "merbabu": {
        "name": "Gunung Merbabu",
        "basecamps": [
            {"jalur": "Selo (Boyolali)", "basecamp_tel": "+6281234567804", "ojek": "Rp 25.000 / trip (Basecamp ➔ Pos 1)", "porter": "Rp 350.000 / hari"},
            {"jalur": "Suwanting (Magelang)", "basecamp_tel": "+6281234567805", "ojek": "Rp 20.000 / trip", "porter": "Rp 350.000 / hari"},
            {"jalur": "Wekas", "basecamp_tel": "+6281234567806", "ojek": "Rp 15.000 / trip", "porter": "Rp 300.000 / hari"}
        ]
    },
    "gede": {
        "name": "Gunung Gede - Pangrango",
        "basecamps": [
            {"jalur": "Cibodas", "basecamp_tel": "+6281234567807", "ojek": "Rp 20.000 / trip", "porter": "Rp 400.000 / hari"},
            {"jalur": "Gunung Putri", "basecamp_tel": "+6281234567808", "ojek": "Rp 15.000 / trip (Basecamp ➔ Tanah Lapang)", "porter": "Rp 400.000 / hari"}
        ]
    },
    "prau": {
        "name": "Gunung Prau",
        "basecamps": [
            {"jalur": "Patak Banteng", "basecamp_tel": "+6281234567809", "ojek": "Rp 20.000 / trip (Pintu Rimba)", "porter": "Rp 250.000 / daytrip"},
            {"jalur": "Dieng / Kalilembu", "basecamp_tel": "+6281234567810", "ojek": "Rp 15.000 / trip", "porter": "Rp 250.000 / daytrip"}
        ]
    },
    "ciremai": {
        "name": "Gunung Ciremai",
        "basecamps": [
            {"jalur": "Apuy (Majalengka)", "basecamp_tel": "+6281234567811", "ojek": "Rp 35.000 / trip (Basecamp ➔ Pos 1 Berod)", "porter": "Rp 350.000 / hari"},
            {"jalur": "Palutungan (Kuningan)", "basecamp_tel": "+6281234567812", "ojek": "Rp 20.000 / trip", "porter": "Rp 350.000 / hari"}
        ]
    }
}

def get_porter_info(mountain_query: str) -> str:
    query = mountain_query.lower()
    match = None
    for k, v in CONTACTS_DB.items():
        if k in query or query in k:
            match = v
            break
            
    if not match:
        match = CONTACTS_DB["sumbing"]
        
    out = [f"🧳 **KONTAK PORTER & TRANSPORT: {match['name'].upper()}**\n"]
    for bc in match["basecamps"]:
        out.append(f"📍 **Jalur {bc['jalur']}**")
        out.append(f"   • 📞 Telp Basecamp/Informasi: `{bc['basecamp_tel']}`")
        out.append(f"   • 🛵 Ojek Local: {bc['ojek']}")
        out.append(f"   • 🎒 Estimasi Tarif Porter: {bc['porter']}")
        out.append("")
        
    out.append("💡 *Catatan: Tarif porter standar membawa beban maksimal 20 kg. Disarankan booking porter H-3 sebelum pendakian.*")
    return "\n".join(out)

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "sumbing"
    print(get_porter_info(q))
