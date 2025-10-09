# 📰 Telegram News Bot

A Python-based Telegram bot that delivers curated business and technology news directly to your chat.  
Built to automate information flow and enhance decision-making efficiency.
(This is a real bot and a real project. It is now working here: t.me/UKToday_News)

---

## 🚀 Features
- Fetches live news from [NewsAPI](https://newsapi.org) (or other APIs)
- Filters and curates content by category, sentiment, or keyword
- Sends news updates automatically via Telegram
- (Optional) AI-enhanced summaries using GPT API

---

## 💼 Business & Data Relevance
- Demonstrates automation and data pipeline creation
- Integrates data APIs for real-time insights
- Enhances business intelligence workflows

---

## 🧠 Tech Stack
- **Language:** Python  
- **Libraries:** `requests`, `python-telegram-bot`, `pandas`, `dotenv`
- **APIs:** NewsAPI, Telegram Bot API  
- **Optional AI:** OpenAI GPT, HuggingFace transformers

---

## ⚙️ Setup Instructions
1. Clone this repository:
  git clone https://github.com/YOUR_USERNAME/telegram-news-bot.git
  cd telegram-news-bot

2. Install dependencies:
pip install -r requirements.txt

3. Create a .env or config.json file with your API keys:
{
  "TELEGRAM_TOKEN": "your_telegram_bot_token",
  "NEWS_API_KEY": "your_news_api_key"
}

4. Run the bot:
python src/main.py
