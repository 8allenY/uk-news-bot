import os
import asyncio
from aiogram import Bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL")

bot = Bot(token=TELEGRAM_TOKEN)

async def test_bot():
    await bot.send_message(chat_id=CHANNEL_ID, text="✅ Bot is alive!")

if __name__ == "__main__":
    asyncio.run(test_bot())
