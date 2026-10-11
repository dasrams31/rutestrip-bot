#!/usr/bin/env python3
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import os
import re
from datetime import datetime

DATA_DIR = "/home/ubuntu/rutestrip-bot"
SEEN_FILE = os.path.join(DATA_DIR, "seen_portal_news.json")

# Kueri live berita pendakian gunung & vulkanik terkini dari Google News Indonesia
SEARCH_QUERIES = [
    "pendakian gunung OR jalur pendakian",
    "simaksi gunung OR kebakaran hutan gunung",
    "status erupsi gunung OR vulkanik gunung",
    "taman nasional gunung indonesia"
]

def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_seen(seen_set):
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        # Simpan maksimal 150 item terakhir agar file tidak membengkak
        trimmed = list(seen_set)[-150:]
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(trimmed, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

import html

def clean_text(text):
    if not text:
        return ""
    # Unescape HTML entities (&nbsp;, &amp;, etc)
    unescaped = html.unescape(str(text))
    # Strip HTML tags
    cleaned = re.sub(r"<[^>]+>", "", unescaped)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

def fetch_live_mountain_news():
    seen_links = load_seen()
    articles = []
    seen_titles = set()

    for q in SEARCH_QUERIES:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(q)}&hl=id&gl=ID&ceid=ID:id"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                xml_content = resp.read()
                root = ET.fromstring(xml_content)
                for item in root.findall(".//item")[:15]:
                    title_elem = item.find("title")
                    raw_title = clean_text(title_elem.text) if title_elem is not None and title_elem.text else ""

                    link_elem = item.find("link")
                    link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""

                    source_elem = item.find("source")
                    source_name = source_elem.text.strip() if source_elem is not None and source_elem.text else ""

                    if " - " in raw_title:
                        parts = raw_title.rsplit(" - ", 1)
                        title_clean = parts[0].strip()
                        if not source_name:
                            source_name = parts[1].strip()
                    else:
                        title_clean = raw_title

                    if not source_name:
                        source_name = "Media Nasional"

                    desc_elem = item.find("description")
                    raw_desc = clean_text(desc_elem.text) if desc_elem is not None and desc_elem.text else ""
                    snippet = raw_desc if len(raw_desc) > 25 else title_clean

                    pub_elem = item.find("pubDate")
                    pub_date = pub_elem.text.strip() if pub_elem is not None and pub_elem.text else ""

                    if title_clean and link and title_clean.lower() not in seen_titles:
                        seen_titles.add(title_clean.lower())
                        is_seen = link in seen_links or title_clean.lower() in seen_links
                        articles.append({
                            "title": title_clean,
                            "source": source_name,
                            "snippet": snippet,
                            "link": link,
                            "pub_date": pub_date,
                            "is_seen": is_seen
                        })
        except Exception:
            continue

    # Prioritaskan berita yang BELUM pernah di-broadcast (unseen)
    unseen_articles = [a for a in articles if not a["is_seen"]]
    selected = unseen_articles[:3] if len(unseen_articles) >= 3 else (unseen_articles + [a for a in articles if a["is_seen"]])[:3]

    if not selected:
        return ""

    # Catat link & judul ke history seen
    for item in selected:
        seen_links.add(item["link"])
        seen_links.add(item["title"].lower())
    save_seen(seen_links)

    lines = []
    for item in selected:
        snip = item["snippet"][:140] + "..." if len(item["snippet"]) > 140 else item["snippet"]
        lines.append(
            f"📌 [{item['source']}] {item['title']}\n"
            f"   \"{snip}\"\n"
            f"   🔗 Baca Selengkapnya: {item['link']}"
        )

    now_wib = datetime.now().strftime("%d %b %Y • %H:%M WIB")

    output = f"""📰 KABAR & BERITA PENDAKIAN MEDIA NASIONAL 🏔️
(Update Otomatis Terkini • {now_wib})

""" + "\n\n".join(lines) + """

---
📢 Channel: @rutestrip
🌐 Portal: https://rutestrip.web.id"""

    return output

if __name__ == "__main__":
    print(fetch_live_mountain_news())
