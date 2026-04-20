import os
import re
import requests
import yt_dlp
import logging
from flask import Flask, request

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

@app.route("/")
def home():
    return "Bot is running!"

# 🔥 METHOD 1: EMBED (fast)
def get_video_embed(insta_url):
    try:
        if not insta_url.endswith("/"):
            insta_url += "/"

        embed_url = insta_url + "embed"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        res = requests.get(embed_url, headers=headers)
        html = res.text

        logging.info("EMBED METHOD USED")

        # Method 1
        match = re.search(r'"video_url":"([^"]+)"', html)
        if match:
            return match.group(1).replace("\\u0026", "&")

        # Method 2
        match = re.search(r'property="og:video" content="([^"]+)"', html)
        if match:
            return match.group(1)

        # Method 3
        match = re.search(r'https://[^"]+\.mp4', html)
        if match:
            return match.group(0)

    except Exception as e:
        logging.error(f"Embed error: {e}")

    return None


# 🔥 METHOD 2: YT-DLP (fallback)
def get_video_ytdlp(insta_url):
    try:
        logging.info("YT-DLP FALLBACK USED")

        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'noplaylist': True,
            'cookiefile': 'cookies.txt'   # 🔥 ADD THIS LINE
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(insta_url, download=False)
            return info.get('url', None)

    except Exception as e:
        logging.error(f"yt-dlp error: {e}")
        return None


# 🔥 MAIN FUNCTION
def get_video_url(insta_url):
    # Try embed first
    video = get_video_embed(insta_url)
    if video:
        return video

    # Fallback to yt-dlp
    return get_video_ytdlp(insta_url)


# 🤖 TELEGRAM WEBHOOK
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

        # Send video
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
