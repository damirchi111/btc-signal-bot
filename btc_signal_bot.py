import requests
import pandas as pd
import talib
import time
import datetime

# تنظیمات تلگرام (اطلاعات شما وارد شده)
TELEGRAM_TOKEN = '7206361586:AAG1xVcBW7dlgM-Ac0iSQwFqfrFTWmgaZfo'
TELEGRAM_CHAT_ID = '-1002671532897'

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=payload)

def get_btc_ohlc():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": "5", "interval": "hourly"}
    res = requests.get(url, params=params).json()
    df = pd.DataFrame(res['prices'], columns=['time', 'price'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df.set_index('time', inplace=True)
    return df

def advanced_analysis(df):
    close = df['price']
    macd, macdsignal, _ = talib.MACD(close)
    rsi = talib.RSI(close)
    upper, middle, lower = talib.BBANDS(close)
    slowk, slowd = talib.STOCH(close, close, close)

    df['open'] = df['price'].shift(1)
    df['high'] = df[['open', 'price']].max(axis=1)
    df['low'] = df[['open', 'price']].min(axis=1)
    df['close'] = df['price']

    engulfing = talib.CDLENGULFING(df['open'], df['high'], df['low'], df['close'])
    hammer = talib.CDLHAMMER(df['open'], df['high'], df['low'], df['close'])

    candle = "بی‌الگو"
    if engulfing.iloc[-1] != 0:
        candle = "Engulfing"
    elif hammer.iloc[-1] != 0:
        candle = "Hammer"

    signal = None
    if macd.iloc[-1] > macdsignal.iloc[-1] and rsi.iloc[-1] < 70 and candle != "بی‌الگو":
        signal = "سیگنال خرید صادر شد (MACD مثبت + RSI متعادل + الگوی کندلی: " + candle + ")"
    elif macd.iloc[-1] < macdsignal.iloc[-1] and rsi.iloc[-1] > 60:
        signal = "سیگنال فروش صادر شد (MACD منفی + RSI بالا)"
    else:
        signal = "در حال حاضر سیگنالی صادر نشده است."

    return signal

def run_smart():
    today = None
    last_signal_type = None

    while True:
        now = datetime.datetime.now()
        try:
            df = get_btc_ohlc()
            signal = advanced_analysis(df)

            if "خرید" in signal:
                signal_type = "buy"
            elif "فروش" in signal:
                signal_type = "sell"
            else:
                signal_type = "none"

            if today != now.date():
                today = now.date()
                last_signal_type = None

            if signal_type != "none" and signal_type != last_signal_type:
                send_telegram_message(f"سیگنال جدید بیت‌کوین:\n\n{signal}")
                last_signal_type = signal_type

        except Exception as e:
            send_telegram_message(f"خطا در اجرای ربات: {e}")

        time.sleep(900)  # هر ۱۵ دقیقه یک‌بار

if __name__ == "__main__":
    run_smart()
