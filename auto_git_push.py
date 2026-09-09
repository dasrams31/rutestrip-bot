#!/usr/bin/env python3
"""
RuteStrip Automatic Git Watcher & Push Daemon
Memantau perubahan file di direktori rutestrip-bot secara realtime.
Setiap kali ada perubahan file (edit/create/delete), script akan melakukan
auto-commit dan auto-push ke GitLab secara otomatis.
"""
import os
import sys
import time
import subprocess
import datetime

REPO_DIR = "/home/ubuntu/rutestrip-bot"
ENV_FILE = "/home/ubuntu/auto_readme_commit.py"
DEBOUNCE_SECONDS = 5  # Jeda batching sebelum commit agar tidak spam
POLL_INTERVAL = 15     # Interval cek berkala (detik)

def get_repo_url():
    token = os.environ.get("GITLAB_TOKEN", "")
    token_file = "/home/ubuntu/.gitlab_token"
    if not token and os.path.exists(token_file):
        with open(token_file, "r") as f:
            token = f.read().strip()
    
    if not token:
        return None
    return f"https://RamsNotes31:{token}@gitlab.com/RamsNotes31/rutestrip-bot.git"

def check_and_push():
    repo_url = get_repo_url()
    if not repo_url:
        print("[AutoPush ERROR] Token GitLab tidak ditemukan.")
        return False

    # 1. Cek apakah ada perubahan (staged, unstaged, untracked)
    res = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_DIR,
        capture_output=True,
        text=True
    )
    changes = res.stdout.strip()
    if not changes:
        return False  # Tidak ada perubahan

    # Filter changes untuk mendapatkan daftar file ringkas
    changed_files = []
    for line in changes.splitlines():
        parts = line.strip().split(maxsplit=1)
        if len(parts) == 2:
            fname = os.path.basename(parts[1])
            if fname not in changed_files:
                changed_files.append(fname)

    summary_files = ", ".join(changed_files[:3])
    if len(changed_files) > 3:
        summary_files += f" (+{len(changed_files)-3} files)"

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")
    commit_msg = f"auto-sync: update {summary_files} ({now_str})"

    print(f"[{now_str}] Terdeteksi perubahan: {summary_files}. Menjalankan auto-push...")

    # 2. Stage all
    subprocess.run(["git", "add", "-A"], cwd=REPO_DIR, check=True)

    # 3. Commit
    commit_res = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=REPO_DIR,
        capture_output=True,
        text=True
    )
    if commit_res.returncode != 0:
        print(f"[AutoPush] Commit ditunda / tidak ada perubahan baru: {commit_res.stderr.strip()}")
        return False

    # 4. Push ke GitLab
    push_res = subprocess.run(
        ["git", "push", repo_url, "main"],
        cwd=REPO_DIR,
        capture_output=True,
        text=True
    )
    if push_res.returncode == 0:
        print(f"[{now_str}] ✅ Sukses push ke GitLab: {commit_msg}")
        return True
    else:
        print(f"[{now_str}] ❌ Gagal push ke GitLab: {push_res.stderr.strip()}")
        return False

def run_inotify_watcher():
    """Menggunakan inotifywait untuk deteksi instan berbasis kernel."""
    exclude_regex = r"(\.git|__pycache__|\.tmp|\.swp|last_cron_seen\.json)"
    cmd = [
        "inotifywait",
        "-m",
        "-r",
        "-e", "modify,create,delete,move",
        "--exclude", exclude_regex,
        REPO_DIR
    ]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        print(f"[*] Inotify watcher aktif di {REPO_DIR}")
        
        while True:
            if proc.stdout is None:
                break
            line = proc.stdout.readline()
            if not line:
                break
            
            # Debounce: tunggu beberapa detik bila ada file lain yang ditulis berurutan
            time.sleep(DEBOUNCE_SECONDS)
            # Flush stdout pipe agar tidak double trigger
            check_and_push()
            
    except Exception as e:
        print(f"[Watcher Exception] {e}, fallback ke polling loop...")
        run_polling_loop()

def run_polling_loop():
    """Fallback polling loop jika inotify tidak berjalan."""
    print(f"[*] Polling loop aktif (interval {POLL_INTERVAL} detik)")
    while True:
        try:
            check_and_push()
        except Exception as e:
            print(f"[Polling Error] {e}")
        time.sleep(POLL_INTERVAL)

def main():
    # Setup git identity
    subprocess.run(["git", "config", "user.name", "RamsNotes31"], cwd=REPO_DIR)
    subprocess.run(["git", "config", "user.email", "ramsnotes31@gmail.com"], cwd=REPO_DIR)

    # Initial check saat startup
    check_and_push()

    # Cek ketersediaan inotifywait
    has_inotify = subprocess.run(["which", "inotifywait"], capture_output=True).returncode == 0
    if has_inotify:
        run_inotify_watcher()
    else:
        run_polling_loop()

if __name__ == "__main__":
    main()
