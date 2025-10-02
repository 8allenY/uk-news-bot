import os
import re
import asyncio
import time
import requests
from datetime import datetime
from collections import deque
from urllib.parse import urlparse, urlunparse
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Переменные окружения
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL")
OWNER_ID = 969709063  # твой реальный chat_id

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Статус
published_count = 0
last_post_time = None
last_title = None
is_paused = False

# Дедупликация
posted_keys = set()

# Очередь для отложенных постов
pending_queue = deque(maxlen=5)

# Топ-10 источников
TOP_SOURCES = "bbc-news,the-guardian-uk,independent,reuters,bloomberg,financial-times,cnn,associated-press,politico,al-jazeera-english"

# Token bucket (лимит публикаций)
bucket_capacity = 2
bucket_interval = 600
bucket_tokens = bucket_capacity
bucket_last_refill = time.time()

def refill_bucket():
    global bucket_tokens, bucket_last_refill
    now = time.time()
    elapsed = now - bucket_last_refill
    if elapsed <= 0:
        return
    rate = bucket_capacity / bucket_interval if bucket_interval > 0 else float('inf')
    bucket_tokens = min(bucket_capacity, bucket_tokens + elapsed * rate)
    bucket_last_refill = now

def can_post_now():
    refill_bucket()
    return bucket_tokens >= 1.0

def consume_token():
    global bucket_tokens
    bucket_tokens = max(0.0, bucket_tokens - 1.0)

def fetch_news(mode="uk"):
    if mode == "uk":
        params = {
            "q": "UK business OR UK politics OR UK society",
            "sources": TOP_SOURCES,
            "pageSize": 20,
            "sortBy": "publishedAt",
            "language": "en",
            "apiKey": NEWS_API_KEY,
        }
    elif mode == "world_politics":
        params = {
            "q": "politics",
            "sources": TOP_SOURCES,
            "pageSize": 20,
            "sortBy": "publishedAt",
            "language": "en",
            "apiKey": NEWS_API_KEY,
        }
    else:
        return []

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

def normalize_url(u: str) -> str:
    try:
        p = urlparse(u)
        clean = urlunparse((p.scheme, p.netloc, p.path, "", "", ""))
        return clean.lower()
    except Exception:
        return (u or "").strip().lower()

def normalize_title(t: str) -> str:
    t = (t or "").lower()
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def make_dedupe_key(article) -> str:
    url = normalize_url(article.get("url", ""))
    title = normalize_title(article.get("title", ""))
    return f"{url}|{title}"

def format_message(article, tag="[UK]"):
    title = article.get("title", "No title")
    raw_content = article.get("content", "")
    description = article.get("description", "")
    text_source = re.sub(r"\[\+\d+ chars\]", "", raw_content if raw_content else description).strip()
    sentences = re.split(r'(?<=[.!?]) +', text_source)
    final_text = " ".join(sentences[:5]).strip() or "No description available"
    url = article.get("url", "")
    return (
        f"*{tag} {title}*\n\n"
        f"📝 {final_text}\n\n"
        f"🔗 [Read more]({url})"
    )

async def send_article(article, tag="[UK]"):
    global published_count, last_post_time, last_title
    message = format_message(article, tag=tag)
    image_url = article.get("urlToImage")
    try:
        if image_url:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=message, parse_mode="Markdown")
        else:
            await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="Markdown")
        published_count += 1
        last_post_time = datetime.now().strftime("%H:%M")
        last_title = article.get("title")
    except Exception as e:
        print("Failed to send article:", e)
        await bot.send_message(chat_id=OWNER_ID, text=f"⚠️ Ошибка отправки статьи: {e}")

async def news_loop():
    while True:
        if is_paused:
            print("⏸️ Публикация приостановлена.")
            await asyncio.sleep(300)
            continue

        print("🔍 Checking for fresh UK and World Politics news...")
        uk_articles = fetch_news("uk")
        world_articles = fetch_news("world_politics")

        fresh_published = False

        for article, tag in [(a, "[UK]") for a in uk_articles] + [(a, "[World]") for a in world_articles]:
            key = make_dedupe_key(article)
            if key in posted_keys:
                continue

            if can_post_now():
                consume_token()
                await send_article(article, tag=tag)
                posted_keys.add(key)
                fresh_published = True
            else:
                print("🚫 Burst limit reached; queuing this article.")
                pending_queue.append((article, tag))

        # Если очередь не пуста и новых статей не было
        if pending_queue and not fresh_published:
            article, tag = pending_queue.popleft()
            key = make_dedupe_key(article)
            if key not in posted_keys and can_post_now():
                consume_token()
                await send_article(article, tag=tag)
                posted_keys.add(key)

        await asyncio.sleep(300)

async def status_report_loop():
    while True:
        refill_bucket()
        status = (
            f"📊 Bot Status:\n"
            f"📰 Published: {published_count} articles\n"
            f"⏰ Last post: {last_post_time or 'None yet'}\n"
            f"💧 Tokens: {bucket_tokens:.2f}/{bucket_capacity} per {bucket_interval}s\n"
            f"📥 Queue: {len(pending_queue)}/5\n"
            f"✅ Bot is running normally"
        )
        try:
            await bot.send_message(chat_id=OWNER_ID, text=status)
        except Exception as e:
            print("Failed to send status:", e)
        await asyncio.sleep(21600)

# Команды
@dp.message(Command(commands=["status"]))
async def status_handler(message: types.Message):
    if message.chat.type == "private" and message.from_user.id == OWNER_ID:
        refill_bucket()
        status = (
            f"📊 Bot Status:\n"
            f"📰 Published: {published_count} articles\n"
            f"⏰ Last post: {last_post_time or 'None yet'}\n"
            f"💧 Tokens: {bucket_tokens:.2f}/{bucket_capacity} per {bucket_interval}s\n"
            f"📥 Queue: {len(pending_queue)}/5\n"
            f"✅ Bot is running normally"
        )
        await message.answer(status)
    else:
        await message.answer("⛔ Команда доступна только владельцу в личке.")

@dp.message(Command(commands=["pause"]))
async def pause_handler(message: types.Message):
    global is_paused
    if message.chat.type == "private" and message.from_user.id == OWNER_ID:
        is_paused = True
        await message.answer("⏸️ Публикация временно приостановлена.")
    else:
        await message.answer("⛔ Команда доступна только владельцу в личке.")

@dp.message(Command(commands=["resume"]))
async def resume_handler(message: types.Message):
    global is_paused
    if message.chat.type == "private" and message.from_user.id == OWNER_ID:
        is_paused = False
        await message.answer("▶️ Публикация возобновлена.")
    else:
        await message.answer("⛔ Команда доступна только владельцу в личке.")

@dp.message(Command(commands=["last"]))
async def last_handler(message: types.Message):
    if message.chat.type == "private" and message.from_user.id == OWNER_ID:
        if last_title and last_post_time:
            await message.answer(f"🕓 Last post at {last_post_time}:\n📰 {last_title}")
        else:
            await message.answer("ℹ️ Ещё не было публикаций.")
    else:
        await message.answer("⛔ Команда доступна только владельцу в личке.")

@dp.message(Command(commands=["set_limit"]))
async def set_limit_handler(message: types.Message):
    global bucket_capacity, bucket_interval, bucket_tokens, bucket_last_refill
    if message.chat.type == "private" and message.from_user.id == OWNER_ID:
        parts = message.text.strip().split()
        if len(parts) != 3:
            await message.answer("ℹ️ Использование: /set_limit <capacity> <interval_seconds>\nПример: /set_limit 2 600")
            return
        try:
            new_capacity = int(parts[1])
            new_interval = int(parts[2])
            if new_capacity <= 0 or new_interval <= 0:
                await message.answer("⚠️ Значения должны быть положительными целыми числами.")
                return
            bucket_capacity = new_capacity
            bucket_interval = new_interval
            bucket_tokens = float(bucket_capacity)  # сбросить бак на полный
            bucket_last_refill = time.time()
            await message.answer(f"✅ Лимит обновлён: {bucket_capacity} пост(а) за {bucket_interval} сек.")
        except ValueError:
            await message.answer("⚠️ Введите целые числа. Пример: /set_limit 2 600")
    else:
        await message.answer("⛔ Команда доступна только владельцу в личке.")

async def startup():
    await bot.send_message(chat_id=OWNER_ID, text="✅ Bot is alive and scanning UK & World Politics headlines...")
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
