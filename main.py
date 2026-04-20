import os
import requests
from flask import Flask, request
import yt_dlp

app = Flask(__name__)

# Get token from environment
BOT_TOKEN = os.environ.get("BOT_TOKEN")

@app.route("/")
def home():
    return "Bot is running!"

# 🎥 Get video URL using yt-dlp
def get_video_url(insta_url):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(insta_url, download=False)
            return info.get('url', None)
    except Exception as e:
        print("Error:", e)
        return None

# 🤖 Telegram webhook
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # Send processing message
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": chat_id, "text": "🔍 Processing..."}
        )

        video_url = get_video_url(text)

        if not video_url:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={"chat_id": chat_id, "text": "❌ Failed to fetch video"}
            )
            return "ok"

        # Send video directly
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
            data={
                "chat_id": chat_id,
                "video": video_url
            }
        )

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
