import os
os.system("playwright install chromium")

from flask import Flask, request
from telegram import Bot, Update
import requests
from bs4 import BeautifulSoup
import os

# 🔐 Get token from environment
BOT_TOKEN = os.environ.get("BOT_TOKEN")

BOT = Bot(token=BOT_TOKEN)
app = Flask(__name__)

from playwright.sync_api import sync_playwright

def get_video_url(insta_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = browser.new_page()

        page.goto("https://fastdl.app/en2")

        # Fill input
        page.fill('input[type="text"]', insta_url)

        # Click download button
        page.click('button')

        # Wait for result
        page.wait_for_timeout(5000)

        video_url = None

        # Try to get video link
        page.wait_for_selector('a[href*=".mp4"]', timeout=10000)

        video_url = page.query_selector('a[href*=".mp4"]').get_attribute("href")

        for link in links:
            href = link.get_attribute("href")
            if href and ".mp4" in href:
                video_url = href
                break

        browser.close()

        return video_url
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
