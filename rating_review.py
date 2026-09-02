import sys
import os
import json
import datetime

REVIEWS_FILE = "/root/reviews.json"
REPO_REVIEWS_FILE = "/root/rutestrip-bot/reviews.json"

DEFAULT_REVIEWS = {
    "merbabu": [
        {"user": "PendakiSantai", "rating": 5, "comment": "Jalur Selo pemandangannya luar biasa, Savana 1 & 2 terbaik!", "date": "2026-02-15"},
        {"user": "RimbaRanger", "rating": 4, "comment": "Jalur Suwanting cukup terjal dan menantang, fisik harus prima.", "date": "2026-02-28"}
    ],
    "sumbing": [
        {"user": "TektokerJawa", "rating": 5, "comment": "Jalur Kaliangkrik tertata rapi, pemandangan puncak sejati keren.", "date": "2026-01-20"},
        {"user": "JejakGunung", "rating": 4, "comment": "Garung lumayan panjang, disarankan camp di Pos 3.", "date": "2026-02-10"}
    ],
    "sindoro": [
        {"user": "AvidHiker", "rating": 4, "comment": "Jalur Kledung trek berbatu, disarankan bawa trekking pole.", "date": "2026-01-11"}
    ],
    "prau": [
        {"user": "PemulaHike", "rating": 5, "comment": "Sangat ramah pemula! Sunrise di Bukit Teletubbies sangat memukau.", "date": "2026-03-01"}
    ],
    "lawu": [
        {"user": "SoloHiker", "rating": 5, "comment": "Jalur Candi Cetho mistis dan indah, Warung Mbok Yem legenda!", "date": "2026-02-05"}
    ]
}

def load_reviews():
    if os.path.exists(REVIEWS_FILE):
        try:
            with open(REVIEWS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_REVIEWS.copy()

def save_reviews(data):
    with open(REVIEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    if os.path.exists("/root/rutestrip-bot"):
        try:
            with open(REPO_REVIEWS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

def format_stars(rating):
    full = "⭐" * int(rating)
    return f"{full} ({rating}/5)"

def get_reviews(gunung_name):
    reviews_db = load_reviews()
    key = gunung_name.lower().strip()
    
    matched_key = None
    if key in reviews_db:
        matched_key = key
    else:
        for k in reviews_db:
            if k in key or key in k:
                matched_key = k
                break
                
    if not matched_key or not reviews_db[matched_key]:
        return f"⭐ **Rating & Review Gunung {gunung_name.capitalize()}**\n\nBelum ada review untuk jalur ini.\nJadilah yang pertama memberi review dengan perintah:\n`review {gunung_name.lower()} <rating 1-5> <ulasan kamu>`"
    
    items = reviews_db[matched_key]
    avg = sum(r['rating'] for r in items) / len(items)
    
    out = []
    out.append(f"⭐ **RATING & REVIEW PENDAKI - {matched_key.upper()}**")
    out.append(f"📊 **Rata-rata Rating:** {format_stars(round(avg, 1))} ({len(items)} Ulasan)\n")
    out.append("💬 **Ulasan Terkini:**")
    
    for i, r in enumerate(reversed(items[-5:]), 1):
        stars = "⭐" * r['rating']
        out.append(f"{i}. **{r['user']}** - {stars}")
        out.append(f"   \"{r['comment']}\" _({r['date']})_")
    
    out.append(f"\n💡 *Ingin menambah review? Ketik:* `review {matched_key} <1-5> <komentar>`")
    return "\n".join(out)

def add_review(gunung_name, rating_str, comment_str, username="PendakiAnon"):
    try:
        rating = int(rating_str)
        if rating < 1 or rating > 5:
            return "⚠️ Rating harus berupa angka antara 1 sampai 5. Contoh: `review merbabu 5 jalurnya keren`"
    except ValueError:
        return "⚠️ Format rating salah. Contoh penggunaan: `review merbabu 5 jalurnya keren sekali`"
        
    if not comment_str.strip():
        return "⚠️ Mohon sertakan komentar/ulasan. Contoh: `review merbabu 5 jalurnya sangat recommended`"

    reviews_db = load_reviews()
    key = gunung_name.lower().strip()
    
    if key not in reviews_db:
        reviews_db[key] = []
        
    new_entry = {
        "user": username,
        "rating": rating,
        "comment": comment_str.strip(),
        "date": datetime.date.today().strftime("%Y-%m-%d")
    }
    
    reviews_db[key].append(new_entry)
    save_reviews(reviews_db)
    
    stars = "⭐" * rating
    return f"✅ **Review Berhasil Ditambahkan!**\n\n🏔️ **Gunung:** {key.capitalize()}\n⭐ **Rating:** {stars} ({rating}/5)\n💬 **Ulasan:** \"{comment_str.strip()}\"\n\nTerima kasih telah berbagi informasi jalur untuk sesama pendaki! 🙏"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Penggunaan: rating_review.py view <gunung> ATAU rating_review.py add <gunung> <rating> <komentar>")
        sys.exit(1)
        
    action = sys.argv[1].lower()
    if action == "view":
        gunung = sys.argv[2] if len(sys.argv) > 2 else "merbabu"
        print(get_reviews(gunung))
    elif action == "add":
        if len(sys.argv) < 4:
            print("⚠️ Format salah. Contoh: rating_review.py add merbabu 5 jalurnya bagus")
        else:
            gunung = sys.argv[2]
            rating = sys.argv[3]
            comment = " ".join(sys.argv[4:])
            print(add_review(gunung, rating, comment))
    else:
        gunung = sys.argv[1]
        if len(sys.argv) >= 3 and sys.argv[2].isdigit():
            rating = sys.argv[2]
            comment = " ".join(sys.argv[3:])
            print(add_review(gunung, rating, comment))
        else:
            print(get_reviews(gunung))
