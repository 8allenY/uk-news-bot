import os
import asyncio
from aiogram import Bot, Dispatcher, types

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message()
async def debug_chat_id(message: types.Message):
    print("👤 Chat ID:", message.chat.id)
    await message.answer("✅ Получено! Проверь логи Railway — там есть твой chat_id.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
