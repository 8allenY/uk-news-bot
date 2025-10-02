import os
import requests
import asyncio
from aiogram import Bot

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL")

bot = Bot(token=TELEGRAM_TOKEN)

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
    print("🔍 Ищу статью для моментальной публикации...")
    params = {
        "q": "UK",
        "pageSize": 20,
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": NEWS_API_KEY
    }

    articles = fetch_news("https://newsapi.org/v2/everything", params)
    print(f"🔎 Найдено статей: {len(articles)}")

    for article in articles:
        print("📰 Заголовок:", article.get("title"))
        url = article.get("url")
        if url and url not in posted_hourly:
            await send_article(article, "🕐 Hourly UK News:")
            posted_hourly.add(url)
            return

    await bot.send_message(chat_id=CHANNEL_ID, text="❌ Нет свежих статей для публикации.")

async def hourly_news_loop():
    await post_one_hourly_article()

    while True:
        await asyncio.sleep(3600)
        await post_one_hourly_article()

async def headline_news_loop():
    while True:
        params = {
            "country": "gb",
            "pageSize": 10,
            "apiKey": NEWS_API_KEY
        }
        articles = fetch_news("https://newsapi.org/v2/top-headlines", params)
        print(f"⚡ Заголовков найдено: {len(articles)}")

        for article in articles:
            print("📰 Заголовок:", article.get("title"))
            url = article.get("url")
            if url and url not in posted_headlines:
                await send_article(article, "⚡ UK Headline:")
                posted_headlines.add(url)

        await asyncio.sleep(300)

async def main():
    await asyncio.gather(
        hourly_news_loop(),
        headline_news_loop()
    )

async def startup():
    await bot.send_message(chat_id=CHANNEL_ID, text="✅ Bot is alive and searching for news...")
    try:
        await main()
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(startup())
