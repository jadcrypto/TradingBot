# D:\Adnan_project\TradingBot\api_client.py
import os
import pandas as pd
from binance.client import Client

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

if not api_key or not api_secret:
    raise EnvironmentError("API_KEY and API_SECRET must be set in the environment variables.")

client = Client(api_key, api_secret)

async def fetch_symbol_data(symbol: str, interval: str) -> pd.DataFrame:
    try:
        candles = client.futures_klines(symbol=symbol, interval=interval, limit=100)
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "num_trades", "taker_buy_base", "taker_buy_quote", "ignore"])
        df["close"] = pd.to_numeric(df["close"])
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol} with interval {interval}: {e}")
        return pd.DataFrame()
