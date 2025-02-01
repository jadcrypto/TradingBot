# D:\Adnan_project\TradingBot\signal_generator.py
import pandas as pd

def trend_following_strategy(df: pd.DataFrame) -> str:
    """
    Trend Following strategy using moving Averages and MACD.
    """
    if 'ma7' not in df or 'ma25' not in df or 'ma99' not in df or 'macd' not in df or df.empty:
        return "WAIT"

    ma7 = df['ma7'].iloc[-1]
    ma25 = df['ma25'].iloc[-1]
    ma99 = df['ma99'].iloc[-1]
    macd = df['macd'].iloc[-1]

    if ma7 > ma25 and ma25 > ma99 and macd > 0 : # Check for uptrend and positive MACD
        return "BUY"
    elif ma7 < ma25 and ma25 < ma99 and macd < 0: # Check for downtrend and negative MACD
        return "SELL"
    return "WAIT"


def overbought_oversold_strategy(df: pd.DataFrame) -> str:
    """
    Overbought/oversold strategy using RSI.
    """
    if 'rsi6' not in df or 'rsi12' not in df or 'rsi24' not in df or df.empty:
        return "WAIT"

    rsi6 = df['rsi6'].iloc[-1]
    rsi12 = df['rsi12'].iloc[-1]
    rsi24 = df['rsi24'].iloc[-1]
   

    if (rsi6 > 70 or rsi12 > 70 or rsi24 > 70):
        return "SELL" # overbought
    elif (rsi6 < 30 or rsi12 < 30 or rsi24 < 30):
         return "BUY" # oversold
    return "WAIT"

def breakout_strategy(df: pd.DataFrame) -> str:
    """
    Breakout Trading Strategy using Bollinger Bands.
    """
    if 'close' not in df or 'bb_up' not in df or 'bb_dn' not in df or df.empty:
        return "WAIT"
    
    close_price = df['close'].iloc[-1]
    bb_up = df['bb_up'].iloc[-1]
    bb_dn = df['bb_dn'].iloc[-1]

    if close_price > bb_up:
        return "BUY"
    elif close_price < bb_dn:
        return "SELL"
    return "WAIT"

def momentum_strategy(df: pd.DataFrame) -> str:
    """
    Momentum Trading Strategy using RSI.
    """
    if 'rsi6' not in df or df.empty:
        return "WAIT"
    
    rsi_current = df['rsi6'].iloc[-1]
    rsi_previous = df['rsi6'].iloc[-2] if len(df) > 1 else rsi_current

    if rsi_current > rsi_previous:
        return "BUY"
    elif rsi_current < rsi_previous:
        return "SELL"
    return "WAIT"
    
def volume_based_strategy(df: pd.DataFrame) -> str:
    """
    Volume Based Trading Strategy using On Balance Volume.
    """
    if 'obv' not in df or df.empty:
        return "WAIT"
    
    obv_current = df['obv'].iloc[-1]
    obv_previous = df['obv'].iloc[-2] if len(df) > 1 else obv_current

    if obv_current > obv_previous:
        return "BUY"
    elif obv_current < obv_previous:
        return "SELL"
    return "WAIT"
    
def macd_dif_dea_crossover_strategy(df: pd.DataFrame) -> str:
    """
    MACD, DIF and DEA crossover strategy.
    """
    if 'macd_dif' not in df or 'macd_dea' not in df or df.empty:
        return "WAIT"
    
    macd_dif = df['macd_dif'].iloc[-1]
    macd_dea = df['macd_dea'].iloc[-1]
    previous_macd_dif = df['macd_dif'].iloc[-2] if len(df) > 1 else macd_dif
    previous_macd_dea = df['macd_dea'].iloc[-2] if len(df) > 1 else macd_dea

    if previous_macd_dif < previous_macd_dea and macd_dif > macd_dea:
        return "BUY"
    elif previous_macd_dif > previous_macd_dea and macd_dif < macd_dea:
        return "SELL"
    return "WAIT"

def bollinger_macd_rsi_strategy(df: pd.DataFrame) -> str:
    """
     Bollinger Bands, MACD, and RSI strategy.
    """
    if 'close' not in df or 'bb_up' not in df or 'bb_dn' not in df or 'macd_dif' not in df or 'rsi12' not in df or df.empty:
       return "WAIT"
   
    close_price = df['close'].iloc[-1]
    bb_up = df['bb_up'].iloc[-1]
    bb_dn = df['bb_dn'].iloc[-1]
    macd_dif = df['macd_dif'].iloc[-1]
    rsi = df['rsi12'].iloc[-1]

    if close_price > bb_up and macd_dif > 0 and rsi > 50:
        return "BUY"
    elif close_price < bb_dn and macd_dif < 0 and rsi < 50:
        return "SELL"
    return "WAIT"
