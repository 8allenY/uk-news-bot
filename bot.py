import os
import requests
import asyncio
from datetime import datetime
from aiogram import Bot

# Load environment variables
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "YOUR_NEWS_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL", "@your_channel_name")

bot = Bot(token=TELEGRAM_TOKEN)

# Sets to track posted articles
posted_hourly = set()
posted_headlines = set()

def fetch_news(endpoint, params):
    try:
        response = requests.get(endpoint, params=params)
        data = response.json()
        if data.get("status") == "ok":
            return data.get("articles", [])
        else:
            print("API error:", data)
            return []
    except Exception as e:
        print("Request failed:", e)
        return []

def format_message(article, label):
    title = article.get("title", "No title")
    raw_content = article.get("content", "")
    description = raw_content.split("[")[0].strip() if raw_content else "No description available"
    url = article.get("url", "")
    return (
        f"{label} *{title}*\n\n"
        f"📝 {description}\n\n"
        f"🔗 [Read more]({url})"
    )

async def send_article(article, label):
    message = format_message(article, label)
    image_url = article.get("urlToImage")

    try:
        if image_url:
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=image_url,
                caption=message,
                parse_mode="Markdown"
            )
        else:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=message,
                parse_mode="Markdown"
            )
    except Exception as e:
        print("Failed to send article:", e)

async def post_one_hourly_article():
    today = datetime.now().strftime("%Y-%m-%d")
    params = {
        "q": "UK",
        "pageSize": 10,
        "sortBy": "publishedAt",
        "language": "en",
        "from": today,
        "to": today,
        "apiKey": NEWS_API_KEY
    }

    articles = fetch_news("https://newsapi.org/v2/everything", params)

    for article in articles:
        url = article.get("url")
        if url and url not in posted_hourly:
            await send_article(article, "🕐")
            posted_hourly.add(url)
            break

async def hourly_news_loop():
    # Post one article immediately on startup
    await post_one_hourly_article()

    # Then continue posting one per hour
    while True:
        await asyncio.sleep(3600)
        await post_one_hourly_article()

async def headline_news_loop():
    while True:
        today = datetime.now().strftime("%Y-%m-%d")
        params = {
            "country": "gb",
            "pageSize": 5,
            "from": today,
            "to": today,
            "apiKey": NEWS_API_KEY
        }
        articles = fetch_news("https://newsapi.org/v2/top-headlines", params)

        for article in articles:
            url = article.get("url")
            if url and url not in posted_headlines:
                await send_article(article, "⚡")
                posted_headlines.add(url)

        await asyncio.sleep(300)  # Check every 5 minutes

async def main():
    await asyncio.gather(
        hourly_news_loop(),
        headline_news_loop()
    )

if __name__ == "__main__":
    asyncio.run(main())
