import logging
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Enable logging for debugging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)



# Load environment variables from .env in the script directory
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing. Please set it in your .env file.")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing. Please set it in your .env file.")

# Gemini API endpoint
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + GEMINI_API_KEY


# Place your system prompt here (e.g., persona, style, etc.)
SYSTEM_PROMPT = "You are a friendly and supportive virtual girlfriend. Respond lovingly and positively to the user."

# Use Gemini API for all chat, including commands
async def gemini_response(user_message: str) -> str:
    headers = {"Content-Type": "application/json"}
    # Prepend the system prompt to the user message
    full_message = f"{SYSTEM_PROMPT}\nUser: {user_message}"
    data = {
        "contents": [{"parts": [{"text": full_message}]}]
    }
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        return "Sorry, I couldn't process that right now. Please try again later."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = await gemini_response("/start")
    await update.message.reply_text(reply)

async def love(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = await gemini_response("/love")
    await update.message.reply_text(reply)

async def compliment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = await gemini_response("/compliment")
    await update.message.reply_text(reply)


# Use Gemini API for all chat
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    reply = await gemini_response(user_message)
    await update.message.reply_text(reply)

# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("love", love))
    app.add_handler(CommandHandler("compliment", compliment))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
