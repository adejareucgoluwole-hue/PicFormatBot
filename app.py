import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from io import BytesIO
import json
import base64

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required!")

# ============= COMMAND HANDLERS =============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"👋 Hello {user.first_name}!\n\n"
        "I'm a multi-function bot. Here's what I can do:\n\n"
        "✍️ **Text Tools:**\n"
        "• /wordcount - Count words in your text\n"
        "• /json - Format JSON data\n"
        "• /base64 - Encode/Decode Base64\n\n"
        "📷 **Image Tools:**\n"
        "• Send me an image to convert or compress\n\n"
        "Use /help to see all available commands."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📋 **Available Commands:**\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/about - About this bot\n"
        "/wordcount - Count words and characters\n"
        "/json - Format and validate JSON\n"
        "/base64 encode/decode - Encode or decode Base64\n\n"
        "📷 **Send any image** to convert or compress it."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "🤖 **Multi-Function Bot v1.0**\n\n"
        "Built with Python and python-telegram-bot library.\n"
        "Deployed on Railway using GitHub."
    )
    await update.message.reply_text(about_text, parse_mode="Markdown")

async def wordcount_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "📝 Please provide some text to count.\n\n"
            "Example: `/wordcount This is my text to count`"
        )
        return
    
    text = " ".join(context.args)
    word_count = len(text.split())
    char_count = len(text)
    char_count_no_spaces = len(text.replace(" ", ""))
    
    response = (
        f"📊 **Word Count Results:**\n\n"
        f"📝 Words: {word_count}\n"
        f"🔤 Characters (with spaces): {char_count}\n"
        f"📏 Characters (without spaces): {char_count_no_spaces}"
    )
    await update.message.reply_text(response, parse_mode="Markdown")

async def json_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "📝 Please provide JSON data to format.\n\n"
            "Example: `/json {\"name\":\"John\",\"age\":30}`"
        )
        return
    
    json_text = " ".join(context.args)
    try:
        parsed = json.loads(json_text)
        formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
        
        if len(formatted) > 4000:
            await update.message.reply_document(
                document=BytesIO(formatted.encode()),
                filename="formatted.json",
                caption="✅ JSON formatted successfully!"
            )
        else:
            await update.message.reply_text(
                f"✅ **Formatted JSON:**\n\n```json\n{formatted}\n```",
                parse_mode="Markdown"
            )
    except json.JSONDecodeError as e:
        await update.message.reply_text(f"❌ Invalid JSON: {str(e)}")

async def base64_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text(
            "🔐 **Base64 Tool**\n\n"
            "Usage:\n"
            "/base64 encode <text> - Encode text to Base64\n"
            "/base64 decode <base64> - Decode Base64 to text\n\n"
            "Examples:\n"
            "/base64 encode Hello World\n"
            "/base64 decode SGVsbG8gV29ybGQ="
        )
        return
    
    action = context.args[0].lower()
    text = " ".join(context.args[1:])
    
    try:
        if action == "encode":
            encoded = base64.b64encode(text.encode()).decode()
            await update.message.reply_text(
                f"🔒 **Encoded (Base64):**\n\n`{encoded}`",
                parse_mode="Markdown"
            )
        elif action == "decode":
            decoded = base64.b64decode(text.encode()).decode()
            await update.message.reply_text(
                f"🔓 **Decoded:**\n\n`{decoded}`",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ Invalid action. Use 'encode' or 'decode'.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ============= IMAGE HANDLERS =============

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image messages - basic processing without PIL."""
    photo = update.message.photo[-1]
    file = await photo.get_file()
    
    # Just acknowledge receipt (no PIL to avoid build issues)
    await update.message.reply_text(
        "📸 **Image Received!**\n\n"
        "⚠️ Image processing is currently disabled due to build issues.\n"
        "The bot is working! Try these commands instead:\n"
        "• /wordcount - Count words\n"
        "• /json - Format JSON\n"
        "• /base64 - Encode/Decode Base64"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages that aren't commands."""
    text = update.message.text
    word_count = len(text.split())
    char_count = len(text)
    
    await update.message.reply_text(
        f"📝 **Message received!**\n\n"
        f"Word count: {word_count}\n"
        f"Character count: {char_count}\n\n"
        f"Try using /help to see available commands."
    )

# ============= MAIN APPLICATION =============

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("wordcount", wordcount_command))
    application.add_handler(CommandHandler("json", json_command))
    application.add_handler(CommandHandler("base64", base64_command))
    
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🤖 Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
