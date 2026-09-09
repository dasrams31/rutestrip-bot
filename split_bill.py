#!/usr/bin/env python3
import sys
import os
import re

# Database default estimasi biaya dasar
DEFAULT_COSTS = {
    "sumbing": {"simaksi": 35000, "ojek": 30000, "parkir": 10000, "makan_hari": 45000, "gas_hari": 10000},
    "merbabu": {"simaksi": 25000, "ojek": 25000, "parkir": 10000, "makan_hari": 45000, "gas_hari": 10000},
    "slamet": {"simaksi": 35000, "ojek": 30000, "parkir": 10000, "makan_hari": 50000, "gas_hari": 10000},
    "sindoro": {"simaksi": 30000, "ojek": 30000, "parkir": 10000, "makan_hari": 45000, "gas_hari": 10000},
    "prau": {"simaksi": 30000, "ojek": 20000, "parkir": 10000, "makan_hari": 40000, "gas_hari": 8000},
    "lawu": {"simaksi": 30000, "ojek": 0, "parkir": 10000, "makan_hari": 45000, "gas_hari": 10000},
    "ciremai": {"simaksi": 50000, "ojek": 35000, "parkir": 10000, "makan_hari": 50000, "gas_hari": 10000},
    "gede": {"simaksi": 50000, "ojek": 20000, "parkir": 15000, "makan_hari": 50000, "gas_hari": 10000},
    "default": {"simaksi": 35000, "ojek": 25000, "parkir": 10000, "makan_hari": 45000, "gas_hari": 10000}
}

def calculate_split_bill(args_list):
    """
    Format input fleksibel:
    - patungan <gunung> <jumlah_orang> <hari> [tambahan k=v atau angka]
    - patungan 4 1500000 (jika langsung total biaya kotor)
    """
    if not args_list:
        return (
            "💡 **PANDUAN KALKULATOR PATUNGAN TIM (SPLIT BILL)**\n\n"
            "Format Penggunaan:\n"
            "• `patungan <gunung> <jml_orang> <jml_hari>`\n"
            "  *Contoh:* `patungan sumbing 4 2`\n\n"
            "• `patungan <gunung> <jml_orang> <jml_hari> carter=<biaya> porter=<biaya> tenda=<biaya>`\n"
            "  *Contoh:* `patungan merbabu 5 2 carter=400000 porter=350000`\n\n"
            "• `patungan <jml_orang> <total_kolektif>`\n"
            "  *Contoh:* `patungan 4 1200000`"
        )

    # Cek mode cepat: patungan <orang> <total_rupiah>
    if len(args_list) == 2 and args_list[0].isdigit() and args_list[1].isdigit():
        people = max(1, int(args_list[0]))
        total_bill = int(args_list[1])
        per_person = total_bill / people
        emergency_fund = total_bill * 0.10
        per_person_with_em = (total_bill + emergency_fund) / people
        
        return (
            f"💰 **KALKULATOR PATUNGAN CEPAT**\n"
            f"👥 Jumlah Anggota: **{people} Orang**\n"
            f"💵 Total Pengeluaran Bersama: **Rp {total_bill:,}**\n"
            f"{'─'*38}\n"
            f"👤 **Iuran Bersih / Orang:** **Rp {int(per_person):,}**\n"
            f"🛡️ **Iuran + Cadangan Darurat (10%):** **Rp {int(per_person_with_em):,}**\n"
            f"*(Dana darurat cadangan: Rp {int(emergency_fund):,} untuk insiden/logistik darurat)*"
        )

    # Parsing parameter gunung
    mountain_key = "default"
    people = 4
    days = 2
    extras = {}

    idx = 0
    if not args_list[0].isdigit():
        mountain_key = args_list[0].lower()
        idx += 1

    if idx < len(args_list) and args_list[idx].isdigit():
        people = max(1, int(args_list[idx]))
        idx += 1

    if idx < len(args_list) and args_list[idx].isdigit():
        days = max(1, int(args_list[idx]))
        idx += 1

    # Extra key=value (carter=300000, sewa_tenda=100000, porter=300000, dll)
    for extra_arg in args_list[idx:]:
        if "=" in extra_arg:
            k, v = extra_arg.split("=", 1)
            v_clean = re.sub(r'[^0-9]', '', v)
            if v_clean:
                extras[k.lower()] = int(v_clean)

    cost_base = DEFAULT_COSTS.get(mountain_key, DEFAULT_COSTS["default"])
    mountain_name = mountain_key.upper() if mountain_key != "default" else "GUNUNG JAWA"

    # Perhitungan Komponen Biaya Per Orang (Variable Costs)
    simaksi_total = cost_base["simaksi"] * people
    ojek_pp_total = cost_base["ojek"] * 2 * people
    logistik_makan_total = cost_base["makan_hari"] * days * people
    gas_total = cost_base["gas_hari"] * days * people

    # Perhitungan Komponen Biaya Rombongan Tetap (Fixed Costs)
    parkir_total = cost_base["parkir"]
    fixed_extras_total = sum(extras.values())

    subtotal_variable = simaksi_total + ojek_pp_total + logistik_makan_total + gas_total
    subtotal_fixed = parkir_total + fixed_extras_total
    grand_total = subtotal_variable + subtotal_fixed

    # Dana Darurat Tim 10%
    dana_darurat = int(grand_total * 0.10)
    total_dengan_darurat = grand_total + dana_darurat

    per_person_base = int(grand_total / people)
    per_person_safe = int(total_dengan_darurat / people)

    lines = [
        f"📊 **RINCIAN PATUNGAN LOGISTIK & TRIP ({mountain_name})**",
        f"👥 Jumlah Tim: **{people} Pendaki** | ⏱️ Durasi: **{days} Hari {days-1} Malam**",
        f"{'─'*42}",
        f"📌 **BIAYA PERORANGAN (VARIABLE COSTS):**",
        f" • Tiket Masuk/Simaksi: Rp {simaksi_total:,} (@Rp {cost_base['simaksi']:,})",
        f" • Ojek Basecamp PP: Rp {ojek_pp_total:,} (@Rp {cost_base['ojek']*2:,})",
        f" • Bahan Makanan Tim: Rp {logistik_makan_total:,} (@Rp {cost_base['makan_hari']*days:,})",
        f" • Gas Kaleng & Bahan Bakar: Rp {gas_total:,} (@Rp {cost_base['gas_hari']*days:,})",
        f"",
        f"📌 **BIAYA BERSAMA / TETAP (FIXED COSTS):**",
        f" • Parkir Kendaraan: Rp {parkir_total:,}"
    ]

    for item, val in extras.items():
        lines.append(f" • Extra ({item.replace('_', ' ').title()}): Rp {val:,}")

    lines.extend([
        f"{'─'*42}",
        f"💵 **SUBTOTAL ANGGARAN TRIP:** **Rp {grand_total:,}**",
        f"🛡️ **DANA CADANGAN DARURAT (10%):** **Rp {dana_darurat:,}**",
        f"⭐ **TOTAL DANA KAS TIM:** **Rp {total_dengan_darurat:,}**",
        f"{'─'*42}",
        f"👤 **IURAN TARGET PER ORANG:**",
        f"👉 **Rp {per_person_safe:,}** *(sudah termasuk kas darurat & logistik)*",
        f"*(Minimal iuran pas-pasan: Rp {per_person_base:,}/orang)*"
    ])

    return "\n".join(lines)

if __name__ == "__main__":
    raw_args = sys.argv[1:]
    print(calculate_split_bill(raw_args))
