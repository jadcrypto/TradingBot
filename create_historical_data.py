# D:\Adnan_project\TradingBot\create_historical_data.py
import asyncio
import os
import pandas as pd
import json
from api_client import fetch_symbol_data
# Load config from JSON or YAML later
config_file_path = "D:\\Adnan_project\\TradingBot\\config.json"

with open(config_file_path, 'r') as f:
    config = json.load(f)

symbols_to_analyze = config['symbols']
timeframes = config['timeframes']

async def main():
    all_data = []
    for symbol in symbols_to_analyze:
        for timeframe in timeframes:
            df = await fetch_symbol_data(symbol, timeframe)
            if not df.empty:
                all_data.append(df)
            else:
                print(f"Could not get data for {symbol} and {timeframe}")
    
    if all_data:
        combined_df = pd.concat(all_data)
        output_path = "D:\\Adnan_project\\TradingBot\\ml_models\\data\\historical_data.csv"
        combined_df.to_csv(output_path, index=False)
        print(f"Historical data saved to {output_path}")
    else:
        print("No data to save")

if __name__ == "__main__":
    asyncio.run(main())
