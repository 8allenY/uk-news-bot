import os
import requests

def get_news(country="gb", page_size=5):
    """Fetches top headlines from NewsAPI."""
    api_key = os.getenv("news_api_key")
    if not api_key:
        raise ValueError("❌ NEWS_API_KEY not set in environment variables.")

    url = f"https://newsapi.org/v2/top-headlines?country={country}&apiKey={api_key}"
    response = requests.get(url)
    data = response.json()

    if "articles" not in data:
        return []

    articles = data["articles"][:page_size]
    news_list = []
    for article in articles:
        title = article.get("title")
        url = article.get("url")
        if title and url:
            news_list.append(f"🗞 {title}\n🔗 {url}")
    return news_list
