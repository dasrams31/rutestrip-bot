import sys
import json

SURVIVAL_DB = {
    "hipotermia": """🧊 **FIRST AID: HIPOTERMIA**
1. **Tanda:** Menggigil hebat, bicara meracau/lambat, bibir kebiruan, lemas.
2. **Tindakan Cepat:**
   • Pindahkan ke dalam tenda/tempat terlindung dari angin.
   • Ganti pakaian basah dengan pakaian kering & hangat.
   • Gunakan matras (isolasi dari tanah) + sleeping bag.
   • Peluk pasien (skin-to-skin / body heat) jika darurat.
   • Beri minuman manis hangat (jika sadar). DILARANG kopi/alkohol!
   • Balut dengan Thermal Blanket (Emergency Foil).""",

    "ams": """🏔️ **FIRST AID: AMS (MOUNTAIN SICKNESS)**
1. **Tanda:** Pusing/sakit kepala hebat, mual, muntah, insomnia, napas pendek.
2. **Tindakan:**
   • ISTIRAHAT total, jangan paksa naik!
   • Minum air putih hangat & konsumsi parasetamol / ibuprofen.
   • Jika gejala berat/tidak membaik 2 jam ➔ **TURUN ELEVASI SEGERA** (turun 300-500m).
   • Gunakan tabung oksigen kaleng (Oxycan).""",

    "tersesat": """🗺️ **SURVIVAL: TERSESAT DI GUNUNG (STOP RULE)**
• **S - Stop:** Berhenti berjalan, jangan panik.
• **T - Think:** Amati sekitar, ingat patokan terakhir.
• **O - Observe:** Cek sisa air, baterai HP, kompas/GPS, cuaca.
• **P - Plan:** Jika ada sinyal ➔ kirim koordinat lokasi ke pos/teman. Jika tidak ada sinyal, ikuti punggungan/aliran air TURUN (jangan naik puncak), buat tanda jejak (batu/pita).""",

    "gigitan_ular": """🐍 **FIRST AID: GIGITAN ULAR / HEWAN BISA**
1. Immobilisasi (ISTIRAHATKAN) anggota tubuh yang tergigit (jangan banyak bergerak agar bisa tidak cepat menyebar).
2. Posisikan luka LEBIH RENDAH dari jantung.
3. **DILARANG:** Menyedot luka, mengikat kencang (tourniquet), atau menoreh pisau!
4. Imobilisasi dengan bidai/spalk sederhana.
5. Evakuasi segera ke basecamp/rumah sakit."""
}

BUDGET_DB = {
    "sumbing": {"simaksi": 35000, "ojek": 30000, "parkir": 10000, "logistik_per_day": 50000},
    "merbabu": {"simaksi": 25000, "ojek": 25000, "parkir": 10000, "logistik_per_day": 50000},
    "gede": {"simaksi": 50000, "ojek": 20000, "parkir": 15000, "logistik_per_day": 60000},
    "prau": {"simaksi": 30000, "ojek": 20000, "parkir": 10000, "logistik_per_day": 45000},
    "ciremai": {"simaksi": 50000, "ojek": 35000, "parkir": 10000, "logistik_per_day": 55000},
    "slamet": {"simaksi": 35000, "ojek": 30000, "parkir": 10000, "logistik_per_day": 50000}
}

def get_survival(topic="hipotermia"):
    t = topic.lower()
    for k in SURVIVAL_DB:
        if k in t:
            return SURVIVAL_DB[k]
    return "Topik tidak ditemukan. Pilih: `hipotermia`, `ams`, `tersesat`, `gigitan_ular`."

def calculate_budget(mountain="sumbing", group_size=3, days=2):
    m_key = mountain.lower()
    b = BUDGET_DB.get(m_key, BUDGET_DB["sumbing"])
    
    simaksi_total = b["simaksi"] * group_size
    ojek_total = b["ojek"] * 2 * group_size  # PP
    parkir = b["parkir"]
    logistik = b["logistik_per_day"] * days * group_size
    
    total_group = simaksi_total + ojek_total + parkir + logistik
    per_person = total_group / group_size
    
    out = [
        f"💰 **ESTIMASI BIAYA PENDAKIAN: {mountain.upper()}**",
        f"👥 Rombongan: {group_size} Orang | ⏱️ Durasi: {days} Hari",
        "-" * 40,
        f"• Simaksi: Rp {simaksi_total:,} (Rp {b['simaksi']:,}/orang)",
        f"• Ojek Basecamp (PP): Rp {ojek_total:,} (Rp {b['ojek']*2:,}/orang)",
        f"• Parkir Kendaraan: Rp {parkir:,}",
        f"• Logistik Makanan: Rp {logistik:,} (Rp {b['logistik_per_day']*days:,}/orang)",
        "-" * 40,
        f"💵 **TOTAL TIM:** **Rp {total_group:,}**",
        f"👤 **ESTIMASI PER ORANG:** **Rp {int(per_person):,}**"
    ]
    return "\n".join(out)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "survival"
    if mode == "survival":
        top = sys.argv[2] if len(sys.argv) > 2 else "hipotermia"
        print(get_survival(top))
    elif mode == "budget":
        m = sys.argv[2] if len(sys.argv) > 2 else "sumbing"
        g = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        d = int(sys.argv[4]) if len(sys.argv) > 4 else 2
        print(calculate_budget(m, g, d))
