import os
import asyncio
from aiogram import Bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL")

bot = Bot(token=TELEGRAM_TOKEN)

async def test_bot():
    await bot.send_message(chat_id=CHANNEL_ID, text="✅ Bot is alive!")

async def startup():
    try:
        await main()
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(startup())

