import os
import requests
import asyncio
from aiogram import Bot

# Load environment variables
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "YOUR_NEWS_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL", "@your_channel_name")

bot = Bot(token=TELEGRAM_TOKEN)

def get_news():
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "UK",
        "pageSize": 10,
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": NEWS_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") == "ok":
        articles = data.get("articles", [])
        print(f"Found {len(articles)} articles.")
        return articles
    else:
        print("Error fetching news:", data)
        return []

async def publish_news():
    articles = get_news()
    if not articles:
        print("No news available for publishing.")
        return

    for index, article in enumerate(articles):
        message = article.get("title", "No title available")
        await bot.send_message(chat_id=CHANNEL_ID, text=message)
        print(f"Published ({index + 1}/10):", message)

        if index < len(articles) - 1:
            await asyncio.sleep(3600)  # Wait 1 hour before posting the next article

if __name__ == "__main__":
    asyncio.run(publish_news())
