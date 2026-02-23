import os
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

def analyze_symbol(symbol, name):
    df = yf.download(symbol, period="5d", interval="15m")

    if df.empty:
        return f"{name}: No data"

    close = df["Close"]

ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1])
ema50 = float(close.ewm(span=50, adjust=False).mean().iloc[-1])
price = float(close.iloc[-1])

delta = close.diff()
gain = delta.clip(lower=0).rolling(14).mean()
loss = -delta.clip(upper=0).rolling(14).mean()

rs = gain / loss
rsi = 100 - (100 / (1 + rs))
rsi_val = float(rsi.iloc[-1])

    # Trend logic
    if (price > ema20) and (ema20 > ema50):
        trend = "Bullish"
        bias = "🟢 Buy dips"
    elif (price < ema20) and (ema20 < ema50):
        trend = "Bearish"
        bias = "🔴 Sell rallies"
    else:
        trend = "Range"
        bias = "🟡 Range trade"

    msg = (
        f"📊 {name} ({datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')})\n"
        f"Price: {price:,.2f}\n"
        f"Trend: {trend}\n"
        f"Bias: {bias}\n"
        f"EMA20: {ema20:,.2f} | EMA50: {ema50:,.2f}\n"
        f"RSI(14): {rsi_val:.1f}"
    )

    return msg

def main():
    msg1 = analyze_symbol("^NDX", "NDX")
    msg2 = analyze_symbol("^N225", "JPN225")

    full_msg = msg1 + "\n\n" + msg2
    send_telegram(full_msg)

if __name__ == "__main__":
    main()
