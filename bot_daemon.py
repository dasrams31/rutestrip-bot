#!/usr/bin/env python3
"""
RuteStrip Dedicated Hiking Assistant Bot Daemon (Natural AI Conversation + Dynamic Hiking Engine)
- Bot: @rutestrip_hikingbot
- Engine: 9Router AI Gateway (ag/gemini-3.7-flash-medium) + SBERT + Open-Meteo + Naismith
- Conversational: Chat bebas, ramah, luas, luwes seputar pendakian gunung di Pulau Jawa
"""

import sys
import os
import json
import time
import urllib.request
import urllib.error
import urllib.parse
import subprocess

BOT_TOKEN = "8904397226:AAE4QF8GRYkGi_HWOQ5tTjZMJxrVDYoyoxc"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
RUTESTRIP_DIR = "/home/ubuntu/rutestrip-bot"
PYTHON_VENV = f"{RUTESTRIP_DIR}/pendakian_env/bin/python"
ROUTER_URL = "http://127.0.0.1:20128/v1/chat/completions"

# Ambil API Key 9Router dari .env
ROUTER_KEY = "sk-0e9803ce3e082f3c035"
if os.path.exists("/home/ubuntu/.hermes/.env"):
    with open("/home/ubuntu/.hermes/.env") as f:
        for l in f:
            if l.startswith("OPENROUTER_API_KEY="):
                ROUTER_KEY = l.strip().split("=", 1)[1]
                break

SYSTEM_PROMPT = """Kamu adalah RuteStrip AI, asisten pintar dan sahabat pendaki gunung di Pulau Jawa (@rutestrip_hikingbot).
Karakter & Gaya Komunikasi:
- Berbicara santai, ramah, hangat, dan luwes dalam bahasa Indonesia (gunakan aku/kamu atau Sobat Pendaki). Tidak kaku seperti robot/mesin perintah.
- Fokus utama dan spesialisasimu HANYALAH seputar pendakian, rimba, rute resmi 55+ GPX gunung di Jawa, perkiraan cuaca pos, estimasi waktu/itinerary, manajemen logistik, peralatan ultralight, tips survival, mitigasi bahaya/hipotermia, serta edukasi Leave No Trace (LNT).
- DILARANG membahas masalah sistem internal, server, infrastruktur VPS, terminal, coding/scripting, atau topik di luar pendakian & alam terbuka.
- Jika pengguna bertanya tentang hal di luar pendakian/alam terbuka (misal server, pemrograman, politik, crypto), tolak dengan sangat ramah, santai, dan arahkan kembali obrolan ke rencana petualangan atau topik gunung.
- Format jawaban rapi, informatif, dan mengalir natural layaknya kawan akrab sesama pecinta alam."""

# In-memory user conversation history
USER_CONVERSATIONS = {}

WELCOME_MSG = """🏔️ <b>Halo Sobat Pendaki! Selamat Datang di RuteStrip AI!</b> 🥾✨

Aku asisten pintar dan teman diskusimu seputar pendakian gunung di seluruh Pulau Jawa. 

Kamu bisa <b>ngobrol bebas</b> denganku layaknya teman sesama pendaki! Tanya apa saja tentang:
🌲 Rekomendasi gunung & jalur sesuai fisikmu
🌦️ Info cuaca & kondisi pos pendakian
🎒 Persiapan logistik, packing, & gear ultralight
⚠️ Tips survival, mitigasi hipotermia, & jalur evakuasi
🗺️ Database rute resmi 55+ GPX jalur gunung

━━━━━━━━━━━━━━━━━━━━
💡 <i>Tips: Kamu bisa langsung ketik pertanyaanmu (contoh: "Halo, rekomendasi gunung pemula di Jateng yang ada pemandangan sabana apa ya?") atau gunakan shortcut perintah seperti /cuaca merbabu, /rekomendasi, /itinerary.</i>

Ada rencana muncak ke mana nih? 🌲⛰️"""

def send_msg(chat_id: int | str, text: str, parse_mode: str = "HTML"):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        # Fallback to plain text if Markdown/HTML parsing error
        try:
            payload["parse_mode"] = ""
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                return json.loads(resp.read().decode())
        except Exception as e2:
            print(f"[-] Error fallback send_msg to {chat_id}: {e2}")
            return None
    except Exception as e:
        print(f"[-] Error send_msg to {chat_id}: {e}")
        return None

def call_9router_ai(chat_id: int | str, user_text: str) -> str:
    """Kirim percakapan natural ke AI Model via 9Router Gateway"""
    if chat_id not in USER_CONVERSATIONS:
        USER_CONVERSATIONS[chat_id] = []
    
    # Pertahankan max 8 turn dialog terakhir
    history = USER_CONVERSATIONS[chat_id][-8:]
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append(msg)
    messages.append({"role": "user", "content": user_text})

    payload = {
        "model": "ag/gemini-3.7-flash-medium",
        "messages": messages,
        "max_tokens": 600,
        "temperature": 0.7
    }

    req = urllib.request.Request(
        ROUTER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ROUTER_KEY}"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw_lines = resp.read().decode("utf-8").split("\n")
            full_text = []
            for line in raw_lines:
                line = line.strip()
                if line.startswith("data:") and not line.startswith("data: [DONE]"):
                    json_str = line[5:].strip()
                    try:
                        chunk = json.loads(json_str)
                        delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if delta:
                            full_text.append(delta)
                    except Exception:
                        pass
            
            ai_reply = "".join(full_text).strip()
            if ai_reply:
                USER_CONVERSATIONS[chat_id].append({"role": "user", "content": user_text})
                USER_CONVERSATIONS[chat_id].append({"role": "assistant", "content": ai_reply})
                return ai_reply
    except Exception as e:
        print(f"[-] 9Router stream error: {e}")

    # Fallback to local SBERT CLI if AI Gateway has network glitch
    res = subprocess.run([PYTHON_VENV, f"{RUTESTRIP_DIR}/pendakian_cli.py", user_text], capture_output=True, text=True)
    if res.stdout and len(res.stdout.strip()) > 5:
        return res.stdout.strip()
    
    return "Maaf Sobat Pendaki, ada sedikit kendala koneksi ke server cuaca & jalur. Coba ulangi pertanyaanmu atau gunakan /help ya!"

def handle_incoming_message(chat_id: int | str, user_text: str) -> str:
    user_text = user_text.strip()
    if not user_text:
        return ""

    cmd = user_text.split()[0].lower()
    args = user_text[len(cmd):].strip()

    if cmd in ["/start", "/help"]:
        return WELCOME_MSG

    # Shortcut Perintah Khusus
    if cmd == "/cuaca":
        gunung = args if args else "Merbabu"
        res = subprocess.run([PYTHON_VENV, f"{RUTESTRIP_DIR}/pendakian_cli.py", "weather", gunung], capture_output=True, text=True)
        return f"<pre>{res.stdout.strip() if res.stdout else 'Data cuaca tidak ditemukan.'}</pre>"

    if cmd == "/rekomendasi":
        query = args if args else "gunung pemula di jawa tengah"
        res = subprocess.run([PYTHON_VENV, f"{RUTESTRIP_DIR}/pendakian_cli.py", "recommend", query], capture_output=True, text=True)
        return f"<pre>{res.stdout.strip() if res.stdout else 'Rekomendasi tidak ditemukan.'}</pre>"

    if cmd == "/itinerary":
        gunung = args if args else "Prau"
        res = subprocess.run([PYTHON_VENV, f"{RUTESTRIP_DIR}/pendakian_cli.py", "itinerary", gunung], capture_output=True, text=True)
        return f"<pre>{res.stdout.strip() if res.stdout else 'Itinerary tidak ditemukan.'}</pre>"

    if cmd == "/gpx":
        res = subprocess.run([PYTHON_VENV, f"{RUTESTRIP_DIR}/pendakian_cli.py", "gpx", args if args else "all"], capture_output=True, text=True)
        return f"<pre>{res.stdout.strip() if res.stdout else 'Daftar GPX tidak ditemukan.'}</pre>"

    if cmd == "/survival":
        res = subprocess.run([PYTHON_VENV, f"{RUTESTRIP_DIR}/pendakian_cli.py", "survival"], capture_output=True, text=True)
        return f"<pre>{res.stdout.strip() if res.stdout else 'Panduan survival tidak ditemukan.'}</pre>"

    if cmd == "/splitbill":
        parts = args.split()
        if len(parts) >= 2:
            total, org = parts[0], parts[1]
            res = subprocess.run([PYTHON_VENV, f"{RUTESTRIP_DIR}/pendakian_cli.py", "splitbill", total, org], capture_output=True, text=True)
            return f"<pre>{res.stdout.strip()}</pre>"
        return "Format: <code>/splitbill &lt;total_biaya&gt; &lt;jumlah_orang&gt;</code>\nContoh: <code>/splitbill 500000 4</code>"

    # Chat Bebas & Improvisasi Cerdas (AI Natural Conversation)
    return call_9router_ai(chat_id, user_text)

def main():
    print("[*] RuteStrip Natural AI Hiking Bot Daemon is running...")
    offset = 0
    while True:
        try:
            url = f"{BASE_URL}/getUpdates?offset={offset}&timeout=20"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode())
                updates = data.get("result", [])
                for u in updates:
                    offset = u["update_id"] + 1
                    
                    # Abaikan update channel post atau update tanpa message user
                    if "channel_post" in u or "edited_channel_post" in u:
                        continue

                    msg = u.get("message")
                    if not msg or "text" not in msg:
                        continue

                    from_user = msg.get("from", {})
                    # Abaikan jika pesan berasal dari bot itu sendiri (is_bot: true)
                    if from_user.get("is_bot", False):
                        continue

                    # Abaikan pesan otomatis telegram service / forward channel
                    if from_user.get("id") in [777000, 1087968824] or from_user.get("username") in ["Telegram", "GroupAnonymousBot"]:
                        continue
                    if "forward_from_chat" in msg or "forward_from" in msg or "sender_chat" in msg:
                        continue

                    # Abaikan jika chat bertipe channel
                    chat = msg.get("chat", {})
                    if chat.get("type") in ["channel"]:
                        continue

                    chat_id = chat.get("id")
                    text = msg["text"]
                    user_name = from_user.get("first_name", "Pendaki")
                    print(f"[>] Chat from {user_name} ({chat_id}): {text}")

                    # Subscriber tracking
                    subs_path = f"{RUTESTRIP_DIR}/subscribers.json"
                    if os.path.exists(subs_path):
                        try:
                            with open(subs_path, "r") as sf:
                                sdata = json.load(sf)
                            if str(chat_id) not in sdata:
                                sdata[str(chat_id)] = {"name": user_name, "joined": time.strftime("%Y-%m-%d %H:%M:%S")}
                                with open(subs_path, "w") as sf:
                                    json.dump(sdata, sf, indent=2)
                        except Exception:
                            pass

                    reply = handle_incoming_message(chat_id, text)
                    if reply:
                        send_msg(chat_id, reply)
        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    main()
