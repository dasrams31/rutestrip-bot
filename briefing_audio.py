import sys
import asyncio
import edge_tts
import subprocess

BRIEFINGS = {
    "sumbing": "Halo sobat pendaki! Niih, briefing santai buat kamu yang mau naik Gunung Sumbing 3.371 mdpl. Trek Sumbing via Kaliangkrik atau Garung itu terkenal nanjak terus tanpa bonus. Persiapkan fisik dan dengkul prima ya! Pemandangan kawah dan Puncak Sejati keren banget. Sumber air minim di atas, wajib bawa air 3 sampai 4 liter per orang. Salam lestari!",
    "merbabu": "Halo sobat pendaki! Niih, briefing santai buat kamu yang mau naik Gunung Merbabu 3.145 mdpl. Merbabu itu terkenal banget sama pemandangan sabana hijaunya yang luas di Pos 3 dan Pos 4 via Selo. Tapi ingat ya, karena jalurnya terbuka, angin di atas bisa kencang banget. Siapkan jaket windproof dan bawa air minimal 3 liter per orang. Tetap utamakan keselamatan, bawa turun sampahmu, dan salam lestari!",
    "gede": "Halo sobat pendaki! Briefing santai pendakian Gunung Gede 2.958 mdpl. Jalur favorit lewat Cibodas atau Gunung Putri. Siap-siap dibuat kagum sama indahnya Alun-Alun Suryakencana. Cuaca di atas sering berubah dan berkabut, selalu sedia jas hujan dan tetap di jalur resmi!",
    "prau": "Halo sobat pendaki! Briefing pendakian Gunung Prau 2.590 mdpl Dieng. Treknya santai dan ramah pemula, cuma 3 sampai 4 jam lewat Patak Banteng. Pemandangan Bukit Teletubbies sama Golden Sunrise-nya juara banget! Jangan lupa bawa baju hangat tebal karena suhu Dieng dingin banget!"
}

def get_briefing_text(mountain="merbabu"):
    key = mountain.lower()
    for k, v in BRIEFINGS.items():
        if k in key or key in k:
            return v
    return BRIEFINGS["merbabu"]

async def generate_indonesian_voice(mountain="merbabu", output_ogg="/tmp/briefing_indonesia.ogg"):
    text = get_briefing_text(mountain)
    voice = "id-ID-ArdiNeural"
    mp3_path = "/tmp/briefing_temp.mp3"
    
    communicate = edge_tts.Communicate(text, voice, rate="-4%", pitch="-1Hz")
    await communicate.save(mp3_path)
    
    subprocess.run(["ffmpeg", "-y", "-i", mp3_path, "-c:a", "libopus", "-b:a", "32k", output_ogg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_ogg

if __name__ == "__main__":
    m = sys.argv[1] if len(sys.argv) > 1 else "merbabu"
    asyncio.run(generate_indonesian_voice(m))
    print(get_briefing_text(m))
