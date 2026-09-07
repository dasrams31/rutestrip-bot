#!/usr/bin/env python3
"""
RuteStrip Daily Backup Checkpoint & Tagging Script
Menyinkronkan data konfigurasi, status database, dan memberikan tag backup harian
lalu mendorongnya ke repositori GitLab (https://gitlab.com/RamsNotes31/rutestrip-bot).
"""
import os
import subprocess
import datetime
import shutil

REPO_DIR = "/home/ubuntu/rutestrip-bot"
HERMES_DIR = "/home/ubuntu/.hermes"

def run_daily_backup():
    now = datetime.datetime.now()
    tag_name = now.strftime("backup-%Y%m%d")
    date_str = now.strftime("%Y-%m-%d %H:%M:%S WIB")

    # 1. Pastikan config & SOUL tersalin ke repo untuk backup
    if os.path.exists(f"{HERMES_DIR}/SOUL.md"):
        shutil.copy(f"{HERMES_DIR}/SOUL.md", f"{REPO_DIR}/SOUL.md")
    
    # 2. Cek apakah ada perubahan file
    subprocess.run(["git", "add", "-A"], cwd=REPO_DIR)
    
    status_res = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_DIR, capture_output=True, text=True)
    if status_res.stdout.strip():
        subprocess.run(["git", "commit", "-m", f"chore(backup): daily system & database snapshot ({date_str})"], cwd=REPO_DIR)
        subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR)

    # 3. Buat Git Tag harian (jika belum ada)
    tag_check = subprocess.run(["git", "tag", "-l", tag_name], cwd=REPO_DIR, capture_output=True, text=True)
    if not tag_check.stdout.strip():
        subprocess.run(["git", "tag", "-a", tag_name, "-m", f"Daily Backup Checkpoint {date_str}"], cwd=REPO_DIR)
        push_tag = subprocess.run(["git", "push", "origin", tag_name], cwd=REPO_DIR, capture_output=True, text=True)
        if push_tag.returncode == 0:
            msg = f"✅ Daily Backup Checkpoint berhasil dibuat & di-push ke GitLab!\n🏷️ Tag: {tag_name}\n⏰ Waktu: {date_str}"
        else:
            msg = f"⚠️ Tag lokal {tag_name} dibuat, push tag gagal: {push_tag.stderr.strip()}"
    else:
        msg = f"ℹ️ Tag {tag_name} sudah ada untuk hari ini. Kode & database sudah tersinkronisasi di branch main."

    print(msg)
    return msg

if __name__ == "__main__":
    run_daily_backup()
