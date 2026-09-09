import json
import os
import time
import uuid
from db_postgres import get_connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHAT_HISTORY_DB = os.path.join(BASE_DIR, "users_chat_sessions.json")

def _load_db():
    if not os.path.exists(CHAT_HISTORY_DB):
        return {}
    try:
        with open(CHAT_HISTORY_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_db(data):
    with open(CHAT_HISTORY_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def save_session_message(user_id: str, session_id: str, sender: str, text: str, meta: dict = None):
    msg_obj = {
        "id": str(uuid.uuid4()),
        "sender": sender,
        "text": text,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "meta": meta or {}
    }

    # Try PostgreSQL first
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT title, messages FROM chat_sessions WHERE session_id = %s;", (session_id,))
        row = cur.fetchone()
        title = text[:35] + ("..." if len(text) > 35 else "")
        if row:
            existing_title = row[0]
            messages = row[1] if isinstance(row[1], list) else json.loads(row[1])
            messages.append(msg_obj)
            if sender == "user" and len(messages) <= 2:
                existing_title = title
            cur.execute("""
            UPDATE chat_sessions
            SET title = %s, messages = %s, updated_at = CURRENT_TIMESTAMP
            WHERE session_id = %s;
            """, (existing_title, json.dumps(messages), session_id))
        else:
            messages = [msg_obj]
            cur.execute("""
            INSERT INTO chat_sessions (session_id, username, title, messages)
            VALUES (%s, %s, %s, %s);
            """, (session_id, user_id, title, json.dumps(messages)))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[PG ERROR] save_session_message fallback: {e}")

    # Dual write to JSON
    db = _load_db()
    if user_id not in db:
        db[user_id] = {}

    if session_id not in db[user_id]:
        db[user_id][session_id] = {
            "session_id": session_id,
            "title": text[:35] + ("..." if len(text) > 35 else ""),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "messages": []
        }

    db[user_id][session_id]["messages"].append(msg_obj)
    if sender == 'user' and len(db[user_id][session_id]["messages"]) <= 2:
        db[user_id][session_id]["title"] = text[:35] + ("..." if len(text) > 35 else "")

    _save_db(db)
    return msg_obj

def get_user_sessions(user_id: str):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT session_id, title, created_at, messages FROM chat_sessions WHERE username = %s ORDER BY created_at DESC;", (user_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        if rows:
            sessions_list = []
            for r in rows:
                msgs = r[3] if isinstance(r[3], list) else (json.loads(r[3]) if r[3] else [])
                sessions_list.append({
                    "session_id": r[0],
                    "title": r[1] or "Percakapan Baru",
                    "created_at": str(r[2]),
                    "message_count": len(msgs)
                })
            return sessions_list
    except Exception as e:
        print(f"[PG ERROR] get_user_sessions fallback: {e}")

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
    sessions_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return sessions_list

def get_session_messages(user_id: str, session_id: str):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT messages FROM chat_sessions WHERE session_id = %s;", (session_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row and row[0]:
            return row[0] if isinstance(row[0], list) else json.loads(row[0])
    except Exception as e:
        print(f"[PG ERROR] get_session_messages fallback: {e}")

    db = _load_db()
    user_sessions = db.get(user_id, {})
    session_data = user_sessions.get(session_id, {})
    return session_data.get("messages", [])

def delete_session(user_id: str, session_id: str):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM chat_sessions WHERE session_id = %s;", (session_id,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[PG ERROR] delete_session: {e}")

    db = _load_db()
    if user_id in db and session_id in db[user_id]:
        del db[user_id][session_id]
        _save_db(db)
        return True
    return False

def clear_all_user_sessions(user_id: str):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM chat_sessions WHERE username = %s;", (user_id,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[PG ERROR] clear_all_user_sessions: {e}")

    db = _load_db()
    if user_id in db:
        db[user_id] = {}
        _save_db(db)
        return True
    return False
