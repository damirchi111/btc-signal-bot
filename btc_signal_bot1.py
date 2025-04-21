
import requests
import time
import pandas as pd
import ta
import os
from telegram import Bot, Update
from telegram.ext import Application, ContextTypes
from flask import Flask
import asyncio
from threading import Thread

app = Flask(__name__)

@app.route('/')
def keep_alive():
    return "Bot is alive!"

# تنظیمات تلگرام
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7206361586:AAG1xVcBW7dlgM-Ac0iSQwFqfrFTWmgaZfo')
TELEGRAM_CHANNEL_ID = int(os.getenv('TELEGRAM_CHANNEL_ID', '-1002671532897'))

# گرفتن قیمت از CoinGecko
def get_ohlc():
    url = 'https://api.coingecko.com/api/v3/coins/bitcoin/ohlc?vs_currency=usd&days=1'
    headers = {'Accept': 'application/json'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 429:
            print("Rate limit exceeded, waiting 60 seconds...")
            time.sleep(60)
            return None
        data = response.json()
        if not data:
            print("No data received from CoinGecko")
            return None
        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close"])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df.dropna()
    except Exception as e:
        print("Error fetching price data:", str(e))
        return None

# تحلیل تکنیکال با RSI، MACD، EMA
def analyze_market(df):
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['ema20'] = ta.trend.EMAIndicator(df['close'], window=20).ema_indicator()

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    signal = None

    if latest['rsi'] < 30 and latest['macd'] > latest['macd_signal'] and latest['close'] > latest['ema20']:
        signal = "سیگنال خرید قوی: RSI زیر ۳۰، کراس مثبت MACD، قیمت بالای EMA20"
    elif latest['rsi'] > 70 and latest['macd'] < latest['macd_signal'] and latest['close'] < latest['ema20']:
        signal = "سیگنال فروش قوی: RSI بالای ۷۰، کراس منفی MACD، قیمت زیر EMA20"

    return signal

# گرفتن قیمت لحظه‌ای
def get_current_price():
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
        response = requests.get(url)
        return response.json()['bitcoin']['usd']
    except:
        return None


async def send_startup_message():
    message = "The bot has restarted and is running."
    await send_signal(message)


async def send_signal(message):
    try:
        async with Application.builder().token(TELEGRAM_BOT_TOKEN).build() as app:
            await app.bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message)
    except Exception as e:
        print("خطا در ارسال پیام:", e)

def price_checker():
    while True:
        try:
            df = get_ohlc()
            if df is not None:
                signal = analyze_market(df)
                if signal:
                    price = get_current_price()
                    if price:
                        full_message = f"{signal}\nقیمت لحظه‌ای: {price} دلار"
                        asyncio.run(send_signal(full_message))
            time.sleep(1800)  # بررسی هر 30 دقیقه
        except Exception as e:
            print(f"Error in price checker: {str(e)}")
            time.sleep(60)

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def start_bot():
    print("ربات فعال شد...")
    flask_thread = Thread(target=run_flask)
    price_thread = Thread(target=price_checker)
    
    flask_thread.daemon = True
    price_thread.daemon = True
    
    flask_thread.start()
    price_thread.start()
    
    # Send the startup message
    asyncio.run(send_startup_message())
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Bot stopped")
