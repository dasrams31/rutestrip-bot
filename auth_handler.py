import json
import os
import time
import hashlib
import uuid

USERS_DB_PATH = "/root/rutestrip-bot/users_auth.json"

def _load_users():
    if not os.path.exists(USERS_DB_PATH):
        return {}
    try:
        with open(USERS_DB_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_users(data):
    with open(USERS_DB_PATH, "w") as f:
        json.dump(data, f, indent=2)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_user(username: str, email: str, password: str, full_name: str = ""):
    users = _load_users()
    username = username.strip().lower()
    email = email.strip().lower()

    if not username or not email or not password:
        return {"status": "error", "message": "Username, email, dan password wajib diisi."}

    for uid, uinfo in users.items():
        if uinfo.get("username") == username:
            return {"status": "error", "message": "Username sudah terdaftar."}
        if uinfo.get("email") == email:
            return {"status": "error", "message": "Email sudah terdaftar."}

    user_id = str(uuid.uuid4())
    raw_token_str = f"{user_id}_{time.time()}"
    token = f"rutestrip_{hashlib.md5(raw_token_str.encode()).hexdigest()}"

    new_user = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "full_name": full_name or username,
        "password_hash": hash_password(password),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "token": token
    }

    users[user_id] = new_user
    _save_users(users)

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
    users = _load_users()
    query = username_or_email.strip().lower()
    pass_hash = hash_password(password)

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
    _save_users(users)

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
    users = _load_users()
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
    return {"status": "error", "valid": False, "message": "Token tidak valid atau telah kedaluwarsa."}
