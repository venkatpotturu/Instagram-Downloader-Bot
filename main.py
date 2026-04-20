from flask import Flask, request
from telegram import Bot, Update
import requests
from bs4 import BeautifulSoup
import os

BOT_TOKEN = "bot_tok"
BOT = Bot(token=BOT_TOKEN)

app = Flask(__name__)

# 🔥 FastDL scraping
def get_video_url(insta_url):
    url = "https://fastdl.app/en2"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://fastdl.app/"
    }

    data = {"url": insta_url}

    response = requests.post(url, headers=headers, data=data)
    soup = BeautifulSoup(response.text, "html.parser")

    for a in soup.find_all("a", href=True):
        if ".mp4" in a["href"]:
            return a["href"]

    return None


@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), BOT)

    if update.message:
        chat_id = update.message.chat.id
        text = update.message.text

        BOT.send_message(chat_id, "🔍 Processing via FastDL...")

        video_url = get_video_url(text)

        if not video_url:
            BOT.send_message(chat_id, "❌ Failed to fetch video")
            return "ok"

        video_data = requests.get(video_url)

        with open("video.mp4", "wb") as f:
            f.write(video_data.content)

        BOT.send_video(chat_id, video=open("video.mp4", "rb"))
        os.remove("video.mp4")

    return "ok"


@app.route("/")
def home():
    return "Bot is running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
