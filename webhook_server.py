from flask import Flask, request, jsonify
from telegram_bot import send_message
from datetime import datetime
import os

app = Flask(__name__)

# Optional: webhook security
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", None)

LAST_ALERTS = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Received payload:", data)
    print("Expected secret:", WEBHOOK_SECRET)
    print("Received secret:", data.get("secret"))
    if not data:
        return jsonify({"status": "error", "msg": "No data"}), 400

    # Security check (recommended)
    if WEBHOOK_SECRET:
        if data.get("secret") != WEBHOOK_SECRET:
            return jsonify({"status": "unauthorized"}), 401

    symbol = data.get("symbol")
    timeframe = data.get("timeframe")
    signal = data.get("signal")
    price = data.get("price")

    key = f"{symbol}_{timeframe}_{signal}"
    now = datetime.utcnow()

    if key in LAST_ALERTS and (now - LAST_ALERTS[key]).seconds < 60:
        return jsonify({"status": "duplicate"}), 200

    LAST_ALERTS[key] = now

    message = (
        f"🚨 EMA Crossover Alert\n\n"
        f"Stock: {symbol}\n"
        f"Timeframe: {timeframe}\n"
        f"Signal: {signal}\n"
        f"Price: {price}\n"
        f"Time: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )

    send_message(message)
    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
