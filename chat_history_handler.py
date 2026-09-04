import json
import os
import time
import uuid

CHAT_HISTORY_DB = "/root/rutestrip-bot/users_chat_history.json"

def _load_history():
    if not os.path.exists(CHAT_HISTORY_DB):
        return {}
    try:
        with open(CHAT_HISTORY_DB, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_history(data):
    with open(CHAT_HISTORY_DB, "w") as f:
        json.dump(data, f, indent=2)

def save_chat_message(user_id: str, sender: str, text: str, meta: dict = None):
    history = _load_history()
    if user_id not in history:
        history[user_id] = []

    msg_obj = {
        "id": str(uuid.uuid4()),
        "sender": sender, # 'user' atau 'bot'
        "text": text,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "meta": meta or {}
    }

    history[user_id].append(msg_obj)

    # Batasi riwayat maksimal 100 pesan terakhir per user agar DB tidak bengkak
    if len(history[user_id]) > 100:
        history[user_id] = history[user_id][-100:]

    _save_history(history)
    return msg_obj

def get_user_chat_history(user_id: str, limit: int = 50):
    history = _load_history()
    user_msgs = history.get(user_id, [])
    return user_msgs[-limit:]

def clear_user_chat_history(user_id: str):
    history = _load_history()
    if user_id in history:
        history[user_id] = []
        _save_history(history)
        return True
    return False
