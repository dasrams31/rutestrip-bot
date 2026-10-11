#!/usr/bin/env python3
"""
RuteStrip Automatic Git Watcher & Push Daemon
Memantau perubahan file di direktori rutestrip-bot secara realtime.
Setiap kali ada perubahan file (edit/create/delete), script akan melakukan
auto-commit dan auto-push ke GitLab dan GitHub secara otomatis.
"""
import os
import sys
import time
import subprocess
import datetime

REPO_DIR = "/home/ubuntu/rutestrip-bot"
DEBOUNCE_SECONDS = 5  # Jeda batching sebelum commit agar tidak spam
POLL_INTERVAL = 15     # Interval cek berkala (detik)

def check_and_push():
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

    print(f"[{now_str}] Terdeteksi perubahan: {summary_files}. Menjalankan auto-push ke GitLab & GitHub...")

    # 2. Setup author & stage all
    subprocess.run(["git", "config", "user.name", "Rama Danadipa"], cwd=REPO_DIR)
    subprocess.run(["git", "config", "user.email", "ramadanadipa.mk2@gmail.com"], cwd=REPO_DIR)
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

    # 4. Push ke origin (GitLab & GitHub)
    push_res = subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=REPO_DIR,
        capture_output=True,
        text=True
    )
    if push_res.returncode == 0:
        print(f"[{now_str}] ✅ Sukses push ke GitLab & GitHub: {commit_msg}")
        return True
    else:
        print(f"[{now_str}] ⚠️ Push output:\n{push_res.stderr.strip()}")
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
            
            # Debounce
            time.sleep(DEBOUNCE_SECONDS)
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
    subprocess.run(["git", "config", "user.name", "Rama Danadipa"], cwd=REPO_DIR)
    subprocess.run(["git", "config", "user.email", "ramadanadipa.mk2@gmail.com"], cwd=REPO_DIR)

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
