import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import requests
from io import BytesIO
from PIL import Image
import json

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required!")

# ============= COMMAND HANDLERS =============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    welcome_text = (
        f"👋 Hello {user.first_name}!\n\n"
        "I'm a multi-function bot. Here's what I can do:\n\n"
        "📷 **Image Tools:**\n"
        "• Send me an image to convert formats\n"
        "• Send me an image to compress it\n"
        "• Send me an image to remove background\n\n"
        "📄 **PDF Tools:**\n"
        "• Send me a PDF to merge\n"
        "• Send me a PDF to split\n\n"
        "✍️ **Text Tools:**\n"
        "• /wordcount - Count words in your text\n"
        "• /plagiarism - Check for plagiarism\n\n"
        "🔧 **Developer Tools:**\n"
        "• /json - Format JSON data\n"
        "• /base64 - Encode/Decode Base64\n\n"
        "Use /help to see all available commands."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message when /help is issued."""
    help_text = (
        "📋 **Available Commands:**\n\n"
        "**General:**\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/about - About this bot\n\n"
        "**Text Tools:**\n"
        "/wordcount - Count words and characters\n"
        "/plagiarism - Check text for plagiarism (coming soon)\n"
        "/summarize - Summarize long text\n\n"
        "**Image Tools:**\n"
        "• Send any image to convert formats (JPG, PNG, WebP)\n"
        "• Send any image to compress it\n"
        "• Send any image to remove background\n\n"
        "**Developer Tools:**\n"
        "/json - Format and validate JSON\n"
        "/base64 [encode/decode] - Encode or decode Base64\n"
        "/qr - Generate QR code from text\n\n"
        "**PDF Tools:**\n"
        "• Send a PDF to merge with others (coming soon)"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send about info."""
    about_text = (
        "🤖 **Multi-Function Bot v1.0**\n\n"
        "Built with Python and python-telegram-bot library.\n"
        "Deployed on Railway using GitHub.\n\n"
        "Features:\n"
        "• Image conversion (JPG, PNG, WebP)\n"
        "• Image compression\n"
        "• JSON formatting\n"
        "• Word counting\n"
        "• And more coming soon!\n\n"
        "📝 Source code available on GitHub."
    )
    await update.message.reply_text(about_text, parse_mode="Markdown")

# ============= TEXT TOOLS =============

async def wordcount_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Count words in the provided text."""
    # Check if text was provided
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
    sentence_count = text.count('.') + text.count('!') + text.count('?')
    
    response = (
        f"📊 **Word Count Results:**\n\n"
        f"📝 Words: {word_count}\n"
        f"🔤 Characters (with spaces): {char_count}\n"
        f"📏 Characters (without spaces): {char_count_no_spaces}\n"
        f"📄 Sentences: {sentence_count}"
    )
    await update.message.reply_text(response, parse_mode="Markdown")

async def json_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Format and validate JSON data."""
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
        
        # If too long, send as file
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
    """Encode or decode Base64."""
    import base64
    
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
    """Handle image messages - convert, compress, or remove background."""
    # Get the largest photo
    photo = update.message.photo[-1]
    file = await photo.get_file()
    
    # Download the image
    image_bytes = await file.download_as_bytearray()
    image = Image.open(BytesIO(image_bytes))
    
    # Create keyboard with options
    keyboard = [
        [
            InlineKeyboardButton("🔄 Convert to JPG", callback_data="convert_jpg"),
            InlineKeyboardButton("🔄 Convert to PNG", callback_data="convert_png"),
        ],
        [
            InlineKeyboardButton("🔄 Convert to WebP", callback_data="convert_webp"),
            InlineKeyboardButton("📦 Compress Image", callback_data="compress"),
        ],
        [
            InlineKeyboardButton("🎨 Remove Background", callback_data="remove_bg"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Store image data in context for later use
    context.user_data['last_image'] = image_bytes
    context.user_data['last_image_format'] = image.format
    
    await update.message.reply_text(
        "📸 **Image Received!**\n\nWhat would you like to do with it?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document messages (PDFs, etc.)."""
    document = update.message.document
    file_name = document.file_name.lower()
    
    if file_name.endswith('.pdf'):
        await update.message.reply_text(
            "📄 **PDF Received!**\n\n"
            "PDF features coming soon:\n"
            "• Merge PDFs\n"
            "• Split PDFs\n"
            "• Convert PDF to Images"
        )
    else:
        await update.message.reply_text(
            f"📁 Received: {document.file_name}\n\n"
            "Currently only PDF files are supported."
        )

# ============= CALLBACK QUERY HANDLERS =============

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses for image processing."""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    user_data = context.user_data
    
    if action == "cancel":
        await query.edit_message_text("❌ Operation cancelled.")
        return
    
    # Check if we have an image
    if 'last_image' not in user_data:
        await query.edit_message_text("❌ No image found. Please send a new image.")
        return
    
    image_bytes = user_data['last_image']
    image = Image.open(BytesIO(image_bytes))
    
    try:
        if action == "convert_jpg":
            # Convert to JPG
            if image.mode in ('RGBA', 'LA', 'P'):
                # Convert to RGB for JPG
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            output = BytesIO()
            image.save(output, format='JPEG', quality=95)
            output.seek(0)
            await query.edit_message_text("✅ Converted to JPG!")
            await query.message.reply_document(
                document=output,
                filename="converted.jpg",
                caption="🔄 Here's your converted image!"
            )
            
        elif action == "convert_png":
            output = BytesIO()
            image.save(output, format='PNG')
            output.seek(0)
            await query.edit_message_text("✅ Converted to PNG!")
            await query.message.reply_document(
                document=output,
                filename="converted.png",
                caption="🔄 Here's your converted image!"
            )
            
        elif action == "convert_webp":
            output = BytesIO()
            image.save(output, format='WEBP', quality=90)
            output.seek(0)
            await query.edit_message_text("✅ Converted to WebP!")
            await query.message.reply_document(
                document=output,
                filename="converted.webp",
                caption="🔄 Here's your converted image!"
            )
            
        elif action == "compress":
            # Compress image
            output = BytesIO()
            image.save(output, format='JPEG', quality=60, optimize=True)
            output.seek(0)
            
            original_size = len(image_bytes)
            compressed_size = output.getbuffer().nbytes
            reduction = ((original_size - compressed_size) / original_size) * 100
            
            await query.edit_message_text(
                f"✅ Compressed!\n"
                f"📊 Original: {original_size//1024}KB\n"
                f"📊 Compressed: {compressed_size//1024}KB\n"
                f"📉 Reduction: {reduction:.1f}%"
            )
            await query.message.reply_document(
                document=output,
                filename="compressed.jpg",
                caption="📦 Here's your compressed image!"
            )
            
        elif action == "remove_bg":
            # Simple background removal (just a placeholder - you'd need an API)
            await query.edit_message_text(
                "🎨 Background removal requires an API key.\n\n"
                "You can use:\n"
                "• remove.bg API\n"
                "• ClipDrop API\n"
                "• Or use the free placeholder below."
            )
            # For demo, just send a placeholder
            await query.message.reply_text(
                "🖼️ Background removed! (This is a placeholder)"
            )
            
        else:
            await query.edit_message_text("❌ Unknown action.")
            
    except Exception as e:
        await query.edit_message_text(f"❌ Error processing image: {str(e)}")
        
    # Clean up
    user_data.pop('last_image', None)

# ============= MAIN APPLICATION =============

def main():
    """Start the bot."""
    # Create the Application with polling mode (no webhook needed)
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("wordcount", wordcount_command))
    application.add_handler(CommandHandler("json", json_command))
    application.add_handler(CommandHandler("base64", base64_command))
    
    # Add message handlers
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # Add callback query handler for inline buttons
    application.add_handler(CallbackQueryHandler(button_callback))

    # Start the bot (using polling - no webhook required)
    print("🤖 Bot is starting...")
    print("ℹ️ Using polling mode - no webhook needed")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
