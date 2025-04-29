import os
import time
import json
import requests
import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from dotenv import load_dotenv
from coinbase import jwt_generator


api_key = "organizations/33254a6a-d414-4419-b21d-4a2d69996031/apiKeys/3d2e4996-8b05-4b2d-bc40-4ff6810aa0eb"
api_secret = "-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEII14tOLbZu2trf3kbpR6NBzivoDbdWlomoZpE0XMFkH7oAoGCCqGSM49\nAwEHoUQDQgAE/e/zEDfLw0p7LxPuGSBsVcz7yr0E3or83IUnWhdjCkAgL/SPfJWH\niHubQQ9+ZLJrccUiFxtYe/ibNyWwYWtejA==\n-----END EC PRIVATE KEY-----\n"
BASE_URL = "https://api.coinbase.com"

if not api_key or not api_secret:
    raise ValueError("🚨 API_KEY or API_SECRET is missing or not set!")



SYMBOL = "BTC-USD"
GRANULARITY = 300
RISK_PERCENT = 0.02
TAKE_PROFIT = 0.04
STOP_LOSS = 0.02

POSITION = None
ENTRY_PRICE = None


def get_jwt(method, path):
    jwt_uri = jwt_generator.format_jwt_uri(method, path)
    return jwt_generator.build_rest_jwt(jwt_uri, api_key, api_secret)


def build_headers(method, path):
    jwt = get_jwt(method, path)
    return {
        "Authorization": f"Bearer {jwt}",
        "Content-Type": "application/json"
    }


def get_btc_balance():
    path = "/api/v3/brokerage/accounts"
    url = f"{BASE_URL}{path}"
    headers = build_headers("GET", path)
    response = requests.get(url, headers=headers)
    try:
        data = response.json()
    except ValueError:
        print("❌ Invalid JSON from Coinbase")
        return 0.0

    for item in data.get("accounts", []):
        if item.get("currency") == "BTC":
            return float(item.get("available_balance", {}).get("value", 0.0))

    print("❌ No BTC balance found.")
    return 0.0


def get_historical_data():
    url = f"https://api.exchange.coinbase.com/products/{SYMBOL}/candles?granularity={GRANULARITY}&limit=100"
    response = requests.get(url)
    df = pd.DataFrame(response.json(), columns=["time", "low", "high", "open", "close", "volume"])
    df = df.sort_values("time")
    df["close"] = df["close"].astype(float)
    return df


def apply_indicators(df):
    df["EMA20"] = EMAIndicator(df["close"], 20).ema_indicator()
    df["EMA50"] = EMAIndicator(df["close"], 50).ema_indicator()
    df["RSI"] = RSIIndicator(df["close"], 14).rsi()
    return df


def check_entry_signal(df):
    if df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1] and \
       df["EMA20"].iloc[-2] <= df["EMA50"].iloc[-2] and \
       40 <= df["RSI"].iloc[-1] <= 60:
        return "SELL"  # since we hold BTC, we sell it
    return None


def place_market_order(side, btc_amount):
    path = "/api/v3/brokerage/orders"
    url = f"{BASE_URL}{path}"
    body = {
        "client_order_id": str(int(time.time() * 1000)),
        "product_id": SYMBOL,
        "side": side.upper(),
        "order_configuration": {
            "market_market_ioc": {
                "base_size": f"{btc_amount:.8f}"
 
            }
        }
    }
    headers = build_headers("POST", path)
    response = requests.post(url, headers=headers, json=body)
    return response.json()


def main():
    global POSITION, ENTRY_PRICE
    while True:
        try:
            df = get_historical_data()
            df = apply_indicators(df)
            signal = check_entry_signal(df)

            current_price = df["close"].iloc[-1]
            print(f"Price: ${current_price:.2f}, EMA20: {df['EMA20'].iloc[-1]:.2f}, EMA50: {df['EMA50'].iloc[-1]:.2f}, RSI: {df['RSI'].iloc[-1]:.2f}")

            if POSITION is None and signal == "SELL":
                btc_balance = get_btc_balance()
                btc_amount = btc_balance * 0.5  # sell 50% of BTC holdings for test
                if btc_amount > 0:
                    result = place_market_order("SELL", btc_amount)
                    ENTRY_PRICE = current_price
                    POSITION = signal
                    print(f"[{signal}] Order placed at ${ENTRY_PRICE:.2f} to sell {btc_amount:.8f} BTC")
                    print("Response:", result)
                else:
                    print("❌ Not enough BTC to sell.")

            else:
                print("No signal or open trade.")

        except Exception as e:
            print("Error:", e)

        print("Sleeping 5 min...\n")
        time.sleep(GRANULARITY)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user (Control + C).")
