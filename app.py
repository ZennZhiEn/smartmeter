from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import openai
import os
import asyncio

# Set API keys from environment
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Create Flask app
app = Flask(__name__)

# Create Telegram Application instance
telegram_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Add command and message handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I’m your AI assistant 🤖 Ask me anything.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    reply = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    await update.message.reply_text(reply.choices[0].message.content)

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Initialize the Telegram app manually
@app.before_first_request
def start_bot():
    asyncio.get_event_loop().run_until_complete(telegram_app.initialize())
    asyncio.get_event_loop().run_until_complete(telegram_app.start())

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK"

@app.route("/", methods=["GET"])
def index():
    return "Bot is alive!"
