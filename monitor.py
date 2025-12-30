import requests
import json
import hashlib
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from datetime import datetime

URLS = {
    "UIT_FANPAGE": "https://www.facebook.com/UIT.Fanpage",
    "UIT_TUYENSINH_FB": "https://www.facebook.com/TuyenSinh.UIT",
    "UIT_LIENTHONG_WEB": "https://tuyensinh.uit.edu.vn/vb2-lien-thong"
}

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_hash(url):
    html = requests.get(url, headers=HEADERS, timeout=30).text
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def load_state():
    with open("state.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def send_email(subject, body):
    sender = "your_email@gmail.com"
    password = "APP_PASSWORD"
    receiver = "phuc.pham.vst@gmail.com"

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

def main():
    old_state = load_state()
    new_state = {}
    changes = []

    for key, url in URLS.items():
        h = fetch_hash(url)
        new_state[key] = h
        if old_state.get(key) != h:
            changes.append(f"- Có cập nhật tại {url}")

    save_state(new_state)

    today = datetime.now().strftime("%d/%m/%Y")

    if not changes:
        send_email(f"[UIT] Không có cập nhật mới ({today})",
                   "Không phát hiện thay đổi trong 24h qua.")
        return

    important = any("tuyen" in c.lower() or "lien" in c.lower() for c in changes)
    subject = "[UIT – QUAN TRỌNG]" if important else "[UIT]"
    subject += f" Cập nhật ({today})"

    body = "Phát hiện thay đổi:\n\n" + "\n".join(changes)
    send_email(subject, body)

if __name__ == "__main__":
    main()
