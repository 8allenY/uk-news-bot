from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from news_handler import get_news

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to /start command."""
    await update.message.reply_text(
        "👋 Hello! Welcome to UK News Bot.\nUse /news to see the latest headlines."
    )

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and send top headlines."""
    try:
        news_list = get_news()
        if not news_list:
            await update.message.reply_text("⚠️ Sorry, no news found.")
            return

        # Show news headlines + “More” button
        keyboard = [[InlineKeyboardButton("More News 🔁", callback_data="more_news")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = "\n\n".join(news_list)
        await update.message.reply_text(message, reply_markup=reply_markup)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error fetching news: {e}")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button press (callback query)."""
    query = update.callback_query
    await query.answer()

    if query.data == "more_news":
        news_list = get_news()
        message = "\n\n".join(news_list)
        await query.edit_message_text(
            text=f"📰 More UK News:\n\n{message}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Refresh 🔄", callback_data="more_news")]]
            ),
        )

