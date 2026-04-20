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

import re
import requests

def get_video_url(insta_url):
    try:
        # Convert to embed URL
        if not insta_url.endswith("/"):
            insta_url += "/"
        embed_url = insta_url + "embed"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        res = requests.get(embed_url, headers=headers)

        # 🔥 Extract video URL from page
        match = re.search(r'"video_url":"([^"]+)"', res.text)

        if match:
            video_url = match.group(1)
            return video_url.replace("\\u0026", "&")

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
