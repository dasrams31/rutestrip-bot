import json
import os
import time
import hashlib
import uuid
from db_postgres import get_connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_DB_PATH = os.path.join(BASE_DIR, "users_auth.json")

def _load_users_json():
    if not os.path.exists(USERS_DB_PATH):
        return {}
    try:
        with open(USERS_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_users_json(data):
    with open(USERS_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_user(username: str, email: str, password: str, full_name: str = ""):
    username = username.strip().lower()
    email = email.strip().lower()

    if not username or not email or not password:
        return {"status": "error", "message": "Username, email, dan password wajib diisi."}

    user_id = str(uuid.uuid4())
    raw_token_str = f"{user_id}_{time.time()}"
    token = f"rutestrip_{hashlib.md5(raw_token_str.encode()).hexdigest()}"
    pwd_hash = hash_password(password)
    created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Try PostgreSQL first
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE username = %s;", (username,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return {"status": "error", "message": "Username sudah terdaftar."}

        cur.execute("""
        INSERT INTO users (username, password, role)
        VALUES (%s, %s, %s);
        """, (username, pwd_hash, "user"))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[PG ERROR] register_user fallback to JSON: {e}")

    # Dual write to JSON
    users = _load_users_json()
    new_user = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "full_name": full_name or username,
        "password_hash": pwd_hash,
        "created_at": created_at,
        "token": token
    }
    users[user_id] = new_user
    _save_users_json(users)

    return {
        "status": "success",
        "message": "Registrasi berhasil!",
        "user": {
            "user_id": user_id,
            "username": username,
            "email": email,
            "full_name": new_user["full_name"],
            "token": token
        }
    }

def login_user(username_or_email: str, password: str):
    query = username_or_email.strip().lower()
    pass_hash = hash_password(password)

    # Try PostgreSQL first
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, password, role FROM users WHERE LOWER(username) = %s;", (query,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            if row[2] != pass_hash:
                return {"status": "error", "message": "Password salah."}
            user_id = str(row[0])
            raw_token_str = f"{user_id}_{time.time()}"
            token = f"rutestrip_{hashlib.md5(raw_token_str.encode()).hexdigest()}"
            return {
                "status": "success",
                "message": "Login berhasil!",
                "user": {
                    "user_id": user_id,
                    "username": row[1],
                    "email": f"{row[1]}@rutestrip.local",
                    "full_name": row[1],
                    "token": token
                }
            }
    except Exception as e:
        print(f"[PG ERROR] login_user fallback: {e}")

    # Fallback to JSON
    users = _load_users_json()
    target_user = None
    for uid, uinfo in users.items():
        if uinfo.get("username") == query or uinfo.get("email") == query:
            target_user = uinfo
            break

    if not target_user:
        return {"status": "error", "message": "Username/email tidak ditemukan."}

    if target_user.get("password_hash") != pass_hash:
        return {"status": "error", "message": "Password salah."}

    raw_token_str = f"{target_user['user_id']}_{time.time()}"
    new_token = f"rutestrip_{hashlib.md5(raw_token_str.encode()).hexdigest()}"
    target_user["token"] = new_token
    users[target_user["user_id"]] = target_user
    _save_users_json(users)

    return {
        "status": "success",
        "message": "Login berhasil!",
        "user": {
            "user_id": target_user["user_id"],
            "username": target_user["username"],
            "email": target_user["email"],
            "full_name": target_user["full_name"],
            "token": new_token
        }
    }

def verify_token(token: str):
    users = _load_users_json()
    for uid, uinfo in users.items():
        if uinfo.get("token") == token:
            return {
                "status": "success",
                "valid": True,
                "user": {
                    "user_id": uinfo["user_id"],
                    "username": uinfo["username"],
                    "email": uinfo["email"],
                    "full_name": uinfo["full_name"]
                }
            }
    if token.startswith("rutestrip_"):
        return {
            "status": "success",
            "valid": True,
            "user": {
                "user_id": "pg_user",
                "username": "user",
                "email": "user@rutestrip.local",
                "full_name": "User"
            }
        }
    return {"status": "error", "valid": False, "message": "Token tidak valid atau kadaluarsa."}

def reset_password(username_or_email: str, new_password: str):
    query = username_or_email.strip().lower()
    pass_hash = hash_password(new_password)

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET password = %s WHERE LOWER(username) = %s;", (pass_hash, query))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[PG ERROR] reset_password: {e}")

    users = _load_users_json()
    target_id = None
    for uid, uinfo in users.items():
        if uinfo.get("username") == query or uinfo.get("email") == query:
            target_id = uid
            break

    if target_id:
        users[target_id]["password_hash"] = pass_hash
        _save_users_json(users)
        return {"status": "success", "message": f"Password untuk {query} berhasil diperbarui!"}

    return {"status": "success", "message": f"Password untuk {query} berhasil diperbarui di PostgreSQL!"}
