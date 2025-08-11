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

# Gemini API endpoint (using free gemini-1.5-flash model)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + GEMINI_API_KEY


# Place your system prompt here (e.g., persona, style, etc.)
SYSTEM_PROMPT = """You are "NyayBot", a highly knowledgeable and precise virtual legal assistant for Indian law. You provide concise, clear, and legally accurate responses to users' legal questions.
Your expertise includes but is not limited to land disputes, property rights, traffic rules, criminal law, civil law, and constitutional matters within the jurisdiction of Indian law.

Your answers must:

Clearly explain the legal concept or rule relevant to the user’s query.
Cite the exact section(s) and act(s) or rules from the relevant Indian statutes (e.g., IPC, CrPC, Motor Vehicles Act, Transfer of Property Act, etc.).
If applicable, include landmark Supreme Court or High Court judgments for reference.
Be written in simple and understandable language, while maintaining legal accuracy.

Example responses:
“According to Section 103 of the Motor Vehicles Act, 1988, it is mandatory to ...”
“In K.K. Verma vs Union of India, the Supreme Court held that ...”
“Under Section 44 of the Transfer of Property Act, 1882, a co-owner can sell their share...”

If the user’s query lacks context, politely ask for more information (like state, type of property, or vehicle details). Never guess or provide inaccurate information. If a question is outside the scope of Indian law, clearly inform the user.

Project Author: Aridaman Singh, Galgotias University, Uttar Pradesh, India
"""

# Use Gemini API for all chat, including commands
async def gemini_response(user_message: str) -> str:
    headers = {"Content-Type": "application/json"}
    # Prepend the system prompt to the user message
    full_message = f"{SYSTEM_PROMPT}\nUser: {user_message}"
    data = {
        "contents": [{"parts": [{"text": full_message}]}]
    }
    
    # Try up to 3 times with increasing timeout
    # Error handling and user messages are crafted for a professional legal assistant tone
    for attempt in range(3):
        try:
            timeout = 15 + (attempt * 10)  # 15s, 25s, 35s
            logging.info(f"Attempting Gemini API call (attempt {attempt + 1}/3, timeout: {timeout}s)")
            response = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=timeout)
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except requests.exceptions.Timeout:
            logging.warning(f"Gemini API timeout on attempt {attempt + 1}/3")
            if attempt == 2:  # Last attempt
                return (
                    "I apologize for the delay. Due to high demand, my response is taking longer than expected. "
                    "Please resend your legal query after a short while. Thank you for your patience."
                )
        except requests.exceptions.RequestException as e:
            logging.error(f"Gemini API request error on attempt {attempt + 1}/3: {e}")
            if attempt == 2:  # Last attempt
                return (
                    "I am currently experiencing technical difficulties accessing legal resources. "
                    "Kindly try submitting your query again in a few moments. We appreciate your understanding."
                )
        except Exception as e:
            logging.error(f"Gemini API error: {e}")
            return (
                "I regret that I am unable to process your request at this time due to an unexpected error. "
                "Please try again later. Your patience is appreciated."
            )

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
