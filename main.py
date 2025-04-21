# main.py
import requests
import time
import telebot
from datetime import datetime

# --- تنظیمات تلگرام ---
TELEGRAM_TOKEN = '7206361586:AAG1xVcBW7dlgM-Ac0iSQwFqfrFTWmgaZfo'
CHAT_ID = -1002671532897
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- پارامترها ---
symbol = "bitcoin"
interval = 60  # هر چند ثانیه یک‌بار بررسی شود
last_signal_time = None

def get_price():
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    response = requests.get(url)
    return response.json()[symbol]['usd']

def send_signal(message):
    bot.send_message(CHAT_ID, f"📢 سیگنال بیت‌کوین:\n{message}")

def advanced_analysis(prices):
    if len(prices) < 20:
        return None
    sma = sum(prices[-20:]) / 20
    last_price = prices[-1]
    change_percent = (last_price - sma) / sma * 100
    if change_percent > 1.5:
        return f"🔼 قیمت از میانگین متحرک بالاتر رفته ({change_percent:.2f}%) - احتمال رشد"
    elif change_percent < -1.5:
        return f"🔻 قیمت از میانگین متحرک پایین‌تر رفته ({change_percent:.2f}%) - احتمال ریزش"
    return None

def run_bot():
    prices = []
    global last_signal_time
    while True:
        try:
            price = get_price()
            prices.append(price)
            if len(prices) > 50:
                prices = prices[-50:]
            now = datetime.utcnow()
            signal = advanced_analysis(prices)

            # ارسال سیگنال روزانه (مثلاً ساعت 10 صبح UTC)
            if now.hour == 10 and now.minute < 5 and (not last_signal_time or last_signal_time.date() != now.date()):
                if signal:
                    send_signal(f"(سیگنال روزانه)\n{signal}")
                    last_signal_time = now

            # سیگنال لحظه‌ای
            elif signal:
                send_signal(signal)
                time.sleep(300)  # برای جلوگیری از ارسال زیاد، 5 دقیقه صبر می‌کنیم

            time.sleep(interval)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_bot()
