from flask import Flask, request
from telegram import Bot, Update
import requests
from bs4 import BeautifulSoup
import os

# 🔐 Get token from environment
BOT_TOKEN = os.environ.get("BOT_TOKEN")

BOT = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# 🔥 FastDL scraping
def get_video_url(insta_url):
    url = "https://fastdl.app/en2"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://fastdl.app",
        "Referer": "https://fastdl.app/en2"
    }

    data = {"url": insta_url}

    response = requests.post(url, headers=headers, data=data)

    # 🔍 DEBUG: print HTML (for fixing issues)
    print(response.text[:1000])

    soup = BeautifulSoup(response.text, "html.parser")

    # 🔥 Improved link detection
    for a in soup.find_all("a", href=True):
        href = a["href"]

        if ("download" in href or ".mp4" in href) and "http" in href:
            return href

    return None


@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # ✅ Send message (sync way)
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": chat_id, "text": "🔍 Processing via FastDL..."}
        )

        video_url = get_video_url(text)

        if not video_url:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={"chat_id": chat_id, "text": "❌ Failed to fetch video"}
            )
            return "ok"

        video_data = requests.get(video_url)

        with open("video.mp4", "wb") as f:
            f.write(video_data.content)

        # ✅ Send video
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
            data={"chat_id": chat_id},
            files={"video": open("video.mp4", "rb")}
        )

        os.remove("video.mp4")

    return "ok"


@app.route("/")
def home():
    return "Bot is running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
