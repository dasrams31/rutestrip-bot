import os
import random
import subprocess
import datetime

BOT_DIR = "/home/ubuntu/rutestrip-bot"
README_PATH = os.path.join(BOT_DIR, "README.md")

COMMIT_MESSAGES = [
    "docs(readme): update system status & telemetry",
    "chore(sync): routine dataset verification",
    "docs: refresh route index and GPX data",
    "chore: daily maintenance and route sync",
    "docs(gpx): update trail statistics and elevation profiles",
    "chore(telemetry): update weather monitoring logs",
    "docs: sync hiking database and itinerary specs"
]

def update_readme_and_push(force=False):
    # If not forced, 60% chance to execute on tick for randomized pattern
    if not force and random.random() > 0.65:
        print("🎲 Random check skipped this tick for natural pattern.")
        return

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")
    
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    badge = f"<!-- AUTO_SYNC_START -->\n> 🔄 *Last Automated Status Check: {now_str}*\n<!-- AUTO_SYNC_END -->"
    
    if "<!-- AUTO_SYNC_START -->" in content:
        import re
        new_content = re.sub(r"<!-- AUTO_SYNC_START -->.*?<!-- AUTO_SYNC_END -->", badge, content, flags=re.DOTALL)
    else:
        new_content = content + "\n\n" + badge

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    token = "glpat-vKNF_tuL6mEnAmDQZe-b_WM6MQpvOjEKdTpubmV1NA8.01.171pct6yb"
    repo_url = f"https://RamsNotes31:{token}@gitlab.com/RamsNotes31/rutestrip-bot.git"
    
    msg = random.choice(COMMIT_MESSAGES) + f" ({now_str})"
    
    subprocess.run(["git", "add", "README.md"], cwd=BOT_DIR)
    subprocess.run(["git", "commit", "-m", msg], cwd=BOT_DIR)
    subprocess.run(["git", "push", repo_url, "main"], cwd=BOT_DIR)
    print(f"✅ Random commit executed & pushed: '{msg}'")

if __name__ == "__main__":
    import sys
    force_flag = "--force" in sys.argv
    update_readme_and_push(force=force_flag)
