# D:\Adnan_project\TradingBot\indicator_calculator.py
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from ta.volatility import BollingerBands
from ta.trend import MACD

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates technical indicators and adds them as columns to the DataFrame."""
    try:
        rsi6 = RSIIndicator(close=df["close"], window=6)
        rsi12 = RSIIndicator(close=df["close"], window=12)
        bb = BollingerBands(close=df["close"], window=20, window_dev=2)
        macd = MACD(close=df["close"], window_slow=26, window_fast=12, window_sign=9)
    
        df['rsi6'] = rsi6.rsi()
        df['rsi12'] = rsi12.rsi()
        df['bb up'] = bb.bollinger_hband()
        df['bb dn'] = bb.bollinger_lband()
        df['bb mid'] = bb.bollinger_mavg()
        df['macd'] = macd.macd()
        df['macd sig'] = macd.macd_signal()
        df['macd dif'] = macd.macd_diff()

        return df
    except Exception as e:
        print(f"Error calculating indicators: {e}")
        return pd.DataFrame()

def calculate_percentage_for_timeframe(df: pd.DataFrame) -> float:
    try:
        bb = BollingerBands(close=df["close"], window=20, window_dev=2)
        rsi_value = RSIIndicator(close=df["close"], window=14)
        ma5 = SMAIndicator(close=df["close"], window=5)
        ma10 = SMAIndicator(close=df["close"], window=10)
        macd_value = MACD(close=df["close"], window_slow=26, window_fast=12, window_sign=9)

        rsi_normalized = (rsi_value.rsi().iloc[-1] - 50) / 50
        hband = bb.bollinger_hband().iloc[-1]
        lband = bb.bollinger_lband().iloc[-1]
        mavg = bb.bollinger_mavg().iloc[-1]
        
        if hband != lband:  # تأكد من أن الفرق ليس صفراً
            bb_normalized = (df["close"].iloc[-1] - mavg) / (hband - lband)
        else:
            bb_normalized = 0  # أو أي قيمة افتراضية أخرى

        ma5_normalized = (df["close"].iloc[-1] - ma5.sma_indicator().iloc[-1]) / df["close"].iloc[-1]
        ma10_normalized = (df["close"].iloc[-1] - ma10.sma_indicator().iloc[-1]) / df["close"].iloc[-1]
        macd_normalized = macd_value.macd().iloc[-1] / 100

        # Assign weights to indicators
        rsi_weight = 0.3
        bb_weight = 0.25
        ma5_weight = 0.15
        ma10_weight = 0.15
        macd_weight = 0.15

        # Calculate weighted sum
        weighted_sum = (rsi_normalized * rsi_weight +
                        bb_normalized * bb_weight +
                        ma5_normalized * ma5_weight +
                        ma10_normalized * ma10_weight +
                        macd_normalized * macd_weight)

        # Scale weighted sum to percentage range
        percentage = weighted_sum * 100

        # Cap percentage at ±100%
        percentage = max(min(percentage, 100), -100)

        return percentage
    except Exception as e:
        print(f"Error calculating percentage: {e}")
        return 0

def determine_signal(percentage: float) -> str:
    buy_threshold = 20  # يمكنك تعديل هذا الحد بناءً على احتياجاتك
    sell_threshold = -20  # يمكنك تعديل هذا الحد بناءً على احتياجاتك

    if percentage >= buy_threshold:
        return "BUY"
    elif percentage <= sell_threshold:
        return "SELL"
    else:
        return "WAIT"
