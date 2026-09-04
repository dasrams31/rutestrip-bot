#!/usr/bin/env python3
import json
import os
import sqlite3

STATE_FILE = "/root/rutestrip-bot/last_cron_seen.json"
IGNORED_CRONS = ["notif-cron-realtime-admin"]

def check_and_report_cron():
    db_path = "/root/.hermes/cron/executions.db"
    if not os.path.exists(db_path):
        return

    last_seen_id = None
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                last_seen_id = json.load(f).get("last_seen_id")
        except Exception:
            pass

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT id, job_id, status, started_at, finished_at, error 
        FROM executions 
        ORDER BY started_at DESC LIMIT 1
    """).fetchall()
    conn.close()

    if not rows:
        return

    latest_exec = rows[0]
    exec_id, job_id, status, started_at, finished_at, error = latest_exec

    # Cek apakah eksekusi cron baru
    if last_seen_id != exec_id:
        job_name = job_id
        jobs_file = "/root/.hermes/cron/jobs.json"
        if os.path.exists(jobs_file):
            try:
                data = json.load(open(jobs_file))
                jobs = data.get("jobs", data.get("cron_jobs", []))
                if isinstance(jobs, dict):
                    jobs = list(jobs.values())
                for j in jobs:
                    if j.get("id") == job_id:
                        job_name = j.get("name", job_id)
                        break
            except Exception:
                pass

        # Update last seen ID terlebih dahulu
        try:
            with open(STATE_FILE, "w") as f:
                json.dump({"last_seen_id": exec_id}, f)
        except Exception:
            pass

        # IGNORE HANYA tugas pengecek diri sendiri (notif-cron-realtime-admin)
        if job_name in IGNORED_CRONS or job_id in IGNORED_CRONS:
            return

        status_emoji = "✅" if status in ["succeeded", "completed", "ok"] else "❌"

        report = (
            f"⚡ **NOTIF REALTIME EKSEKUSI CRONJOB** {status_emoji}\n\n"
            f"📌 **Nama Tugas:** {job_name}\n"
            f"🆔 **Job ID:** `{job_id}`\n"
            f"📊 **Status:** `{status.upper()}`\n"
            f"⏰ **Waktu Eksekusi:** `{started_at[:19].replace('T', ' ')} WIB`\n"
        )
        if error:
            report += f"⚠️ **Catatan Error:** `{error}`\n"

        report += "\n📝 *Eksekusi cronjob telah selesai diproses oleh Hermes Scheduler.*"

        print(report)

if __name__ == "__main__":
    check_and_report_cron()
