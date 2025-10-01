import os
import requests
import time
from telegram import Bot

# Токен бота (из BotFather)
TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

# ID или @username канала
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL", "@UKToday_News")

# Интервал (для теста сделаем 60 секунд)
POST_INTERVAL = 60

bot = Bot(token=TOKEN)

# Функция для получения новостей
def get_latest_news():
    url = "https://newsapi.org/v2/everything"
    params = {
        "country": "gb",   # UK
        "pageSize": 10,
        "apiKey": os.getenv("NEWS_API_KEY", "YOUR_NEWS_API_KEY")
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        return data.get("articles", [])
    except Exception as e:
        print("Ошибка получения новостей:", e)
        return []

# Функция публикации новости
def post_news(article):
    title = article.get("title", "No title")
    url = article.get("url", "")
    message = f"📰 {title}\n\nRead more: {url}"
    try:
        bot.send_message(chat_id=CHANNEL_ID, text=message)
        print("Опубликовано:", title)
    except Exception as e:
        print("Ошибка публикации:", e)

def main():
    # сразу публикуем первую новость
    articles = get_latest_news()
    if articles:
        post_news(articles[0])
    else:
        print("Нет новостей для публикации")

    # потом обычный цикл (каждую минуту)
    while True:
        time.sleep(POST_INTERVAL)
        articles = get_latest_news()
        if articles:
            post_news(articles[0])

if __name__ == "__main__":
    main()

