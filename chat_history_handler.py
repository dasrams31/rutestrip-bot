import json
import os
import time
import uuid

CHAT_HISTORY_DB = "/home/ubuntu/rutestrip-bot/users_chat_sessions.json"

def _load_db():
    if not os.path.exists(CHAT_HISTORY_DB):
        return {}
    try:
        with open(CHAT_HISTORY_DB, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_db(data):
    with open(CHAT_HISTORY_DB, "w") as f:
        json.dump(data, f, indent=2)

def save_session_message(user_id: str, session_id: str, sender: str, text: str, meta: dict = None):
    db = _load_db()
    if user_id not in db:
        db[user_id] = {}

    # Jika session_id belum ada, buatkan sesi percakapan baru
    if session_id not in db[user_id]:
        title = text[:35] + ("..." if len(text) > 35 else "")
        db[user_id][session_id] = {
            "session_id": session_id,
            "title": title,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "messages": []
        }

    msg_obj = {
        "id": str(uuid.uuid4()),
        "sender": sender,
        "text": text,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "meta": meta or {}
    }

    db[user_id][session_id]["messages"].append(msg_obj)

    # Update judul sesi dari pesan pertama pengguna jika masih bawaan
    if sender == 'user' and len(db[user_id][session_id]["messages"]) <= 2:
        db[user_id][session_id]["title"] = text[:35] + ("..." if len(text) > 35 else "")

    _save_db(db)
    return msg_obj

def get_user_sessions(user_id: str):
    db = _load_db()
    user_sessions = db.get(user_id, {})
    sessions_list = []
    for s_id, s_data in user_sessions.items():
        sessions_list.append({
            "session_id": s_id,
            "title": s_data.get("title", "Percakapan Baru"),
            "created_at": s_data.get("created_at"),
            "message_count": len(s_data.get("messages", []))
        })
    # Sortir dari sesi terbaru ke lama
    sessions_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return sessions_list

def get_session_messages(user_id: str, session_id: str):
    db = _load_db()
    user_sessions = db.get(user_id, {})
    session_data = user_sessions.get(session_id, {})
    return session_data.get("messages", [])

def delete_session(user_id: str, session_id: str):
    db = _load_db()
    if user_id in db and session_id in db[user_id]:
        del db[user_id][session_id]
        _save_db(db)
        return True
    return False

def clear_all_user_sessions(user_id: str):
    db = _load_db()
    if user_id in db:
        db[user_id] = {}
        _save_db(db)
        return True
    return False
