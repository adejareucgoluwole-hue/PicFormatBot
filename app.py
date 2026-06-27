from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "running", "service": "Telegram Bot"})

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming messages from Telegram"""
    data = request.get_json()
    
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        # Route the command to the right function
        response_text = process_command(text, data["message"])
        
        # Send the response back to the user
        send_telegram_message(chat_id, response_text)
    
    return jsonify({"status": "ok"}), 200

def process_command(text, message_data):
    """Process different commands and return the response"""
    if text == "/start":
        return "Welcome! Send me an image and I'll convert it!"
    elif text == "/help":
        return "Available commands: /start, /help"
    # Add your other functions here
    else:
        return f"You sent: {text}"

def send_telegram_message(chat_id, text):
    """Send a message to the user who initiated the conversation"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
