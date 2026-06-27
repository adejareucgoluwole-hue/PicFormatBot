from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "running", "service": "Telegram Bot"})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

@app.route("/test", methods=["GET"])
def test():
    msg = request.args.get("msg", "Test message from bot")
    send_telegram_message(msg)
    return jsonify({"status": "sent", "message": msg})

@app.route("/signal", methods=["POST"])
def webhook():
    # Verify webhook secret if set
    if WEBHOOK_SECRET:
        secret = request.headers.get("X-Webhook-Secret")
        if secret != WEBHOOK_SECRET:
            return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    if data:
        message = format_message(data)
        send_telegram_message(message)
    
    return jsonify({"status": "received"}), 200

def format_message(data):
    """Format the incoming webhook data into a readable message"""
    parts = []
    for key, value in data.items():
        if isinstance(value, float):
            value = f"{value:.2f}"
        parts.append(f"*{key}*: {value}")
    return "\n".join(parts)

def send_telegram_message(text):
    """Send a message to the configured Telegram chat"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
