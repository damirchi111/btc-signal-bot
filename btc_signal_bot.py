import time
import requests
import pandas as pd
import talib
from binance.client import Client

# اطلاعات واقعی تلگرام و بایننس (تو فعلاً فقط اطلاعات بایننس رو باید وارد کنی)
BINANCE_API_KEY = 'gBWOijV60TWM49D9ZKSYk7VDJOIHohuTj5LTsVsbQZJhzmdIPbAGQVqGdcTGVUMH'
BINANCE_API_SECRET = 'lU8yCjpyAbOZWm7F0OPzlMlK6vYIi5DvBLoqHW0Xu5onRPQeqrI9Z4n3h8DIRvrK'
TELEGRAM_TOKEN = '7206361586:AAG1xVcBW7dlgM-Ac0iSQwFqfrFTWmgaZfo'
TELEGRAM_CHAT_ID = '-1002671532897'

# اتصال به بایننس
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

# ارسال پیام به تلگرام
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)

# گرفتن داده‌های بازار
def get_data(symbol="BTCUSDT", interval='1h', lookback='100'):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=int(lookback))
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                       'close_time', 'quote_asset_volume', 'num_trades',
                                       'taker_buy_base', 'taker_buy_quote', 'ignore'])
    df['close'] = df['close'].astype(float)
    return df

# تحلیل و بررسی بازار
def analyze(df):
    close = df['close']
    rsi = talib.RSI(close, timeperiod=14)
    ema_9 = talib.EMA(close, timeperiod=9)
    ema_21 = talib.EMA(close, timeperiod=21)
    macd, macdsignal, _ = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

    signal = None
    if rsi.iloc[-1] < 35 and ema_9.iloc[-1] > ema_21.iloc[-1] and macd.iloc[-1] > macdsignal.iloc[-1]:
        signal = "سیگنال خرید (LONG)"
    elif rsi.iloc[-1] > 70 and ema_9.iloc[-1] < ema_21.iloc[-1] and macd.iloc[-1] < macdsignal.iloc[-1]:
        signal = "سیگنال فروش (SHORT)"
    return signal

# اجرای مداوم ربات
def run_bot():
    while True:
        try:
            df = get_data()
            signal = analyze(df)
            if signal:
                send_telegram_message(f"سیگنال بیت‌کوین: {signal}")
            else:
                print("سیگنالی صادر نشد.")
            time.sleep(900)  # هر ۱۵ دقیقه
        except Exception as e:
            send_telegram_message(f"خطا در ربات: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_bot()
