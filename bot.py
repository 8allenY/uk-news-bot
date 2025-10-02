import os
import requests
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Переменные окружения
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL")
OWNER_USERNAME = "@allicksis"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

posted_articles = set()
published_count = 0
last_post_time = None
last_title = None
is_paused = False

def fetch_news():
    params = {
        "q": "UK business OR UK politics OR UK society",
        "pageSize": 20,
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": NEWS_API_KEY
    }
    try:
        response = requests.get("https://newsapi.org/v2/everything", params=params)
        data = response.json()
        if data.get("status") == "ok":
            return data.get("articles", [])
        else:
            print("API error:", data)
            return []
    except Exception as e:
        print("Request failed:", e)
        return []

def format_message(article):
    title = article.get("title", "No title")
    raw_content = article.get("content", "")
    description = article.get("description", "")

    if raw_content and "[+" not in raw_content:
        final_text = raw_content.strip()
    elif description:
        final_text = description.strip()
    else:
        final_text = "No description available"

    url = article.get("url", "")
    return (
        f"*{title}*\n\n"
        f"📝 {final_text}\n\n"
        f"🔗 [Read more]({url})"
    )

async def send_article(article):
    global published_count, last_post_time, last_title
    message = format_message(article)
    image_url = article.get("urlToImage")
    url = article.get("url")

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
        posted_articles.add(url)
        published_count += 1
        last_post_time = datetime.now().strftime("%H:%M")
        last_title = article.get("title")
    except Exception as e:
        print("Failed to send article:", e)
        await bot.send_message(chat_id=OWNER_USERNAME, text=f"⚠️ Ошибка отправки статьи: {e}")

async def news_loop():
    while True:
        if is_paused:
            print("⏸️ Публикация приостановлена.")
            await asyncio.sleep(300)
            continue

        print("🔍 Checking for fresh UK business/political/social news...")
        articles = fetch_news()
        print(f"🔎 Found {len(articles)} articles")

        if not articles:
            await bot.send_message(chat_id=OWNER_USERNAME, text="⚠️ NewsAPI не вернул статьи")

        for article in articles:
            print("📰 Заголовок:", article.get("title"))
            url = article.get("url")
            if url and url not in posted_articles:
                await send_article(article)

        await asyncio.sleep(300)

async def status_report_loop():
    while True:
        status = (
            f"📊 Bot Status:\n"
            f"📰 Published: {published_count} articles\n"
            f"⏰ Last post: {last_post_time or 'None yet'}\n"
            f"✅ Bot is running normally"
        )
        try:
            await bot.send_message(chat_id=OWNER_USERNAME, text=status)
        except Exception as e:
            print("Failed to send status:", e)
        await asyncio.sleep(21600)  # каждые 6 часов

# Команды в личке
@dp.message(Command(commands=["status"]))
async def status_handler(message: types.Message):
    if message.chat.type == "private" and message.from_user.username == "allicksis":
        status = (
            f"📊 Bot Status:\n"
            f"📰 Published: {published_count} articles\n"
            f"⏰ Last post: {last_post_time or 'None yet'}\n"
            f"✅ Bot is running normally"
        )
        await message.answer(status)
    else:
        await message.answer("⛔ Команда доступна только @allicksis в личке.")

@dp.message(Command(commands=["pause"]))
async def pause_handler(message: types.Message):
    global is_paused
    if message.chat.type == "private" and message.from_user.username == "allicksis":
        is_paused = True
        await message.answer("⏸️ Публикация временно приостановлена.")
    else:
        await message.answer("⛔ Команда доступна только @allicksis в личке.")

@dp.message(Command(commands=["resume"]))
async def resume_handler(message: types.Message):
    global is_paused
    if message.chat.type == "private" and message.from_user.username == "allicksis":
        is_paused = False
        await message.answer("▶️ Публикация возобновлена.")
    else:
        await message.answer("⛔ Команда доступна только @allicksis в личке.")

@dp.message(Command(commands=["last"]))
async def last_handler(message: types.Message):
    if message.chat.type == "private" and message.from_user.username == "allicksis":
        if last_title and last_post_time:
            await message.answer(f"🕓 Last post at {last_post_time}:\n📰 {last_title}")
        else:
            await message.answer("ℹ️ Ещё не было публикаций.")
    else:
        await message.answer("⛔ Команда доступна только @allicksis в личке.")

async def startup():
    await bot.send_message(chat_id=OWNER_USERNAME, text="✅ Bot is alive and scanning UK headlines...")
    try:
        await asyncio.gather(
            dp.start_polling(bot),
            news_loop(),
            status_report_loop()
        )
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(startup())
