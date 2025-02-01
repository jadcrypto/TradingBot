# D:\Adnan_project\TradingBot\trade_logger.py
import pandas as pd
import os

trades_file = "D:\\Adnan_project\\TradingBot\\trades.csv"

def log_trade(timestamp, symbol, type, price):
    """تسجيل عملية التداول في ملف CSV"""
    df = pd.DataFrame([{'timestamp': timestamp, 'symbol': symbol, 'type': type, 'price': price}])
    if os.path.exists(trades_file):
      df.to_csv(trades_file, mode='a', header=False, index=False)
    else:
      df.to_csv(trades_file, mode='w', header=True, index=False)
