#!/usr/bin/env python3
"""
RuteStrip Telegram Broadcast Helper
Dispatches broadcasts to Channel (@rutestrip), Groups, and/or Users based on target configuration.
"""

import os
import json
import urllib.request
import urllib.parse
import time

BOT_TOKEN = "8904397226:AAHSb48P3i4d1F1UqLg6yUf6YF8VvL_tXfU"
OFFICIAL_CHANNEL = "@rutestrip"
SUBSCRIBERS_PATH = "/home/ubuntu/rutestrip-bot/subscribers.json"

def get_bot_token() -> str:
    env_token = os.getenv("RUTESTRIP_BOT_TOKEN")
    if env_token:
        return env_token
    daemon_path = "/home/ubuntu/rutestrip-bot/bot_daemon.py"
    if os.path.exists(daemon_path):
        try:
            with open(daemon_path) as f:
                for line in f:
                    if line.strip().startswith("BOT_TOKEN ="):
                        return line.split("=", 1)[1].strip().strip('"\'')
        except Exception:
            pass
    return BOT_TOKEN

def send_telegram_msg(chat_id: str | int, text: str, parse_mode: str = "HTML") -> bool:
    token = get_bot_token()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
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
            res = json.loads(resp.read().decode())
            return res.get("ok", False)
    except Exception:
        # Fallback to Markdown or plain text
        for fallback_mode in ["Markdown", ""]:
            try:
                payload["parse_mode"] = fallback_mode
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=12) as resp:
                    res = json.loads(resp.read().decode())
                    if res.get("ok", False):
                        return True
            except Exception:
                pass
        return False

def send_telegram_message(bot_token, chat_id, text, parse_mode="HTML"):
    return send_telegram_msg(chat_id, text, parse_mode)

def broadcast_to_subscribers(message: str, targets: str = "all"):
    """
    targets options:
    - 'channel': only Official Channel (@rutestrip)
    - 'groups' / 'group': all group chats (-100...)
    - 'users' / 'user' / 'dm': all personal user chats
    - 'channel_and_users': Official Channel + personal user chats
    - 'channel_and_groups': Official Channel + group chats
    - 'all': Official Channel + group chats + personal user chats
    """
    targets_lower = str(targets).lower().strip()
    
    send_targets = set()
    
    # Check if channel is included
    if targets_lower in ["channel", "all", "channel_and_users", "channel_and_groups"]:
        send_targets.add(OFFICIAL_CHANNEL)
        
    subs = {}
    if os.path.exists(SUBSCRIBERS_PATH):
        try:
            with open(SUBSCRIBERS_PATH, "r", encoding="utf-8") as f:
                subs = json.load(f)
        except Exception as e:
            print(f"[-] Gagal membaca subscribers: {e}")

    for cid_raw in subs.keys():
        cid = str(cid_raw).strip()
        if not cid or cid in ["777000", "Telegram"]:
            continue
            
        if cid == OFFICIAL_CHANNEL:
            if targets_lower in ["channel", "all", "channel_and_users", "channel_and_groups"]:
                send_targets.add(cid)
            continue
            
        # Group chat detection
        if cid.startswith("-"):
            if targets_lower in ["group", "groups", "all", "channel_and_groups", "channel_and_users"]:
                send_targets.add(cid)
        else:
            # Personal user DM
            if targets_lower in ["users", "user", "dm", "all", "channel_and_users", "channel_and_groups"]:
                send_targets.add(cid)

    print(f"[*] Mengirim siaran ke {len(send_targets)} target (mode: {targets})...")
    success_count = 0
    fail_count = 0

    for target_id in sorted(send_targets, key=str):
        ok = send_telegram_msg(target_id, message)
        if ok:
            success_count += 1
            print(f"[✓] Terkirim ke {target_id}")
        else:
            fail_count += 1
            print(f"[✗] Gagal kirim ke {target_id}")
        time.sleep(0.35)

    print(f"[=] Selesai broadcast: {success_count} sukses, {fail_count} gagal.")
    return success_count, fail_count

if __name__ == "__main__":
    import sys
    msg = sys.argv[1] if len(sys.argv) > 1 else "⚡ Tes broadcast helper multi-target"
    tgt = sys.argv[2] if len(sys.argv) > 2 else "channel"
    broadcast_to_subscribers(msg, targets=tgt)
