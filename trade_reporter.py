# D:\Adnan_project\TradingBot\trade_reporter.py
import pandas as pd
import os
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
# Constants for file paths
TEMPLATES_DIR = "D:\\Adnan_project\\TradingBot\\templates"

def organize_trade_data(df: pd.DataFrame,symbol: str="All", timeframe: str="All", signal: str="All") -> dict:
    """Organizes trade data by timestamp."""
    
    if df.empty:
          return {}
    
    organized_trades = {}
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by='timestamp')
    
    for index, row in df.iterrows():
            timestamp = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            trade_info = {
              'type': row['type'],
               'symbol': row['symbol'],
                'price': row['price']
                }

            if timestamp not in organized_trades:
              organized_trades[timestamp] = []
            organized_trades[timestamp].append(trade_info)

    return organized_trades

def generate_html_report(trades: dict, output_dir: str, symbol_filter: str="All", timeframe_filter: str="All", signal_filter: str="All") -> str:
    """Generates an HTML report from trade data."""
    
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("report.html")
    
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"trade_report_{current_time}.html"
    file_path = os.path.join(output_dir, file_name)
    
    html_content = template.render(trades=trades, file_name=file_name, symbol_filter=symbol_filter, timeframe_filter=timeframe_filter, signal_filter=signal_filter)
    
    with open(file_path, "w", encoding="utf-8") as f:
      f.write(html_content)
    return file_name
    
def generate_trade_report(data_file: str, output_dir: str):
    """Main function to generate trade report."""
    trades_df = pd.read_csv(data_file) if os.path.exists(data_file) else pd.DataFrame()
    
    if trades_df.empty:
      print("No trades available")
      return
    
    organized_trades = organize_trade_data(trades_df)
    report_file = generate_html_report(organized_trades, output_dir)
    archive_reports(output_dir, report_file)

def archive_reports(output_dir: str, report_file: str):
    """Archives generated reports."""
    archive_dir = os.path.join(output_dir, "archive")
    os.makedirs(archive_dir, exist_ok=True)
    source_path = os.path.join(output_dir, report_file)
    destination_path = os.path.join(archive_dir, report_file)
    
    os.rename(source_path, destination_path)

if __name__ == "__main__":
    # Example usage (for testing purposes)
    trades_file = "D:\\Adnan_project\\TradingBot\\trades.csv"
    output_dir = "D:\\Adnan_project\\TradingBot\\reports"
    generate_trade_report(trades_file, output_dir)
    print("Report generated successfully")
