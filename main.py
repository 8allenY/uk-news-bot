import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from telegram_bot import start, news, button

def main():
    token = os.getenv("TELE_TOKEN")
    if not token:
        print("❌ TELE_TOKEN not set in environment variables.")
        return

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CallbackQueryHandler(button))

    print("🤖 UK News Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

