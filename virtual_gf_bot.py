import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hey love ❤️! I’m your virtual girlfriend 🤗. "
        "Type /love to get some love or just say hi!"
    )

async def love(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "I love you so much 😘💖! You’re the best thing ever happened to me! 💕"
    )

async def compliment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "You’re smart, handsome, and you make my heart flutter 🥰✨!"
    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower()
    if "miss you" in user_message:
        await update.message.reply_text("I miss you too, baby 🥹💕")
    elif "good night" in user_message:
        await update.message.reply_text("Good night love! Dream of me 😴💤❤️")
    else:
        await update.message.reply_text("Tell me more 🫶. I love listening to you!")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("love", love))
    app.add_handler(CommandHandler("compliment", compliment))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("Bot is running...")

    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    import asyncio

    nest_asyncio.apply()

    asyncio.get_event_loop().run_until_complete(main())
