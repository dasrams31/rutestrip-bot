import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor, Json

DB_CONFIG = {
    "dbname": "rutestrip",
    "user": "rutestrip_user",
    "password": "rutestrip_pass",
    "host": "localhost",
    "port": 5432
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    # Create tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        role VARCHAR(50) DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_sessions (
        session_id VARCHAR(100) PRIMARY KEY,
        username VARCHAR(100),
        title TEXT,
        messages JSONB DEFAULT '[]'::jsonb,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS subscribers (
        chat_id BIGINT PRIMARY KEY,
        name VARCHAR(255),
        subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id SERIAL PRIMARY KEY,
        mountain_key VARCHAR(100) NOT NULL,
        user_name VARCHAR(100) NOT NULL,
        rating INT NOT NULL,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS recommendation_history (
        id SERIAL PRIMARY KEY,
        query TEXT,
        recommendation JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("Database tables initialized successfully.")

def migrate_json_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    conn = get_connection()
    cur = conn.cursor()

    # Migrate users_auth.json
    users_path = os.path.join(base_dir, "users_auth.json")
    if os.path.exists(users_path):
        try:
            with open(users_path, "r", encoding="utf-8") as f:
                users_data = json.load(f)
                for username, uinfo in users_data.items():
                    pwd = uinfo.get("password", "")
                    role = uinfo.get("role", "user")
                    cur.execute("""
                    INSERT INTO users (username, password, role)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (username) DO UPDATE SET password = EXCLUDED.password;
                    """, (username, pwd, role))
            print("Users data migrated.")
        except Exception as e:
            print(f"Users migration error: {e}")

    # Migrate subscribers.json
    sub_path = os.path.join(base_dir, "subscribers.json")
    if os.path.exists(sub_path):
        try:
            with open(sub_path, "r", encoding="utf-8") as f:
                subs_data = json.load(f)
                if isinstance(subs_data, list):
                    for sub in subs_data:
                        chat_id = sub if isinstance(sub, (int, str)) else sub.get("chat_id")
                        name = sub.get("name", "User") if isinstance(sub, dict) else "User"
                        if chat_id:
                            cur.execute("""
                            INSERT INTO subscribers (chat_id, name)
                            VALUES (%s, %s)
                            ON CONFLICT (chat_id) DO NOTHING;
                            """, (int(chat_id), name))
            print("Subscribers data migrated.")
        except Exception as e:
            print(f"Subscribers migration error: {e}")

    # Migrate reviews.json
    reviews_path = os.path.join(base_dir, "reviews.json")
    if os.path.exists(reviews_path):
        try:
            with open(reviews_path, "r", encoding="utf-8") as f:
                rev_data = json.load(f)
                if isinstance(rev_data, list):
                    for r in rev_data:
                        cur.execute("""
                        INSERT INTO reviews (mountain_key, user_name, rating, comment)
                        VALUES (%s, %s, %s, %s);
                        """, (r.get("mountain_key", "general"), r.get("user_name", "Anon"), r.get("rating", 5), r.get("comment", "")))
            print("Reviews data migrated.")
        except Exception as e:
            print(f"Reviews migration error: {e}")

    conn.commit()
    cur.close()
    conn.close()
    print("All JSON data migrated to PostgreSQL.")

if __name__ == "__main__":
    init_db()
    migrate_json_data()
