# D:\Adnan_project\TradingBot\trading_bot.py
import asyncio
import os
import json
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import pandas as pd

# import modules for separation of concern
from api_client import fetch_symbol_data
from indicator_calculator import calculate_percentage_for_timeframe, determine_signal
from sentiment_analyzer import get_ai_response, get_named_entities
from trade_logger import log_trade
from trade_reporter import generate_trade_report, generate_html_report, archive_reports, organize_trade_data # Import functions directly
from ml_models.predictive_model import load_historical_data, prepare_data, train_model, validate_model, inference, load_model
from ml_models.rl_agent import QLearningAgent, run_rl_agent

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Load config from JSON or YAML later
config_file_path = "D:\\Adnan_project\\TradingBot\\config.json"

with open(config_file_path, 'r') as f:
    config = json.load(f)

symbols_to_analyze = config['symbols']
timeframes = config['timeframes']
trades_file = config['trades_file']
output_dir = config['output_dir']

#Load and train Predictive model
historical_data_file = config['historical_data_file']
df = load_historical_data(historical_data_file)

if df is not None:
    X_train, X_test, y_train, y_test, scaler = prepare_data(df, 'target')

    if X_train is not None:
        model = train_model(X_train, y_train)
        accuracy = validate_model(model, X_test, y_test)
        print(f"Model Accuracy {accuracy}")
    else:
         print("Error preparing the data")
else:
    print("Error: Could not load historical data")
    model = None
    scaler = None


#RL agent setup
state_size = 5
action_size = 3
agent = QLearningAgent(state_size, action_size)
num_episodes = 10
#Run RL agent to train
if df is not None:
    df =  calculate_indicators(df)
    run_rl_agent(df, agent, num_episodes)

loaded_model = load_model()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            results = []
            for symbol in symbols_to_analyze:
                try:
                    symbol_results = {"symbol": symbol, "timeframes": {}}
                    for timeframe in timeframes:
                         symbol_data = await fetch_symbol_data(symbol, timeframe)
                         if symbol_data.empty:
                             await websocket.send_json({"error": f"Failed to fetch data for {symbol} with interval {timeframe}."})
                             continue
                         
                         percentage = calculate_percentage_for_timeframe(symbol_data)
                         signal = determine_signal(percentage)
                         
                         # Predictive Model Logic
                         if loaded_model and scaler:
                            prediction = inference(loaded_model, symbol_data.iloc[[-1]], scaler)
                            if prediction:
                                prediction_label = "Increase" if prediction[0] == 1 else "Decrease"
                                ai_prompt = f"Analyze the trading signal for {symbol} with percentage {percentage} in timeframe {timeframe}, the prediction is {prediction_label}."
                            else:
                                ai_prompt = f"Analyze the trading signal for {symbol} with percentage {percentage} in timeframe {timeframe}."
                         else:
                            ai_prompt = f"Analyze the trading signal for {symbol} with percentage {percentage} in timeframe {timeframe}."

                         ai_response = get_ai_response(ai_prompt)
                         ner_entities = get_named_entities(ai_prompt)
                         
                         symbol_results["timeframes"][timeframe] = {
                            "signal": signal,
                            "percentage": percentage,
                            "price": symbol_data["close"].iloc[-1],
                            "ai_response": ai_response,
                            "ner_entities": ner_entities
                         }
                         current_time = datetime.now()
                         if signal != "WAIT":
                              log_trade(current_time, symbol, signal, symbol_data["close"].iloc[-1])

                    results.append(symbol_results)
                except Exception as e:
                     print(f"Error processing {symbol}: {e}")
                     await websocket.send_json({"error": f"Error processing {symbol}: {e}"})

            try:
               await websocket.send_json({"results": results})
               print("Data sent to the HTML page.")
            except Exception as e:
                 print(f"Error sending data: {e}")

            await asyncio.sleep(10)

    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"error": f"WebSocket error: {e}"})
        except RuntimeError as e:
            print(f"Send json error : {e}")
        finally:
            if websocket.client_state != 3: #  3 is the "CLOSED" state
                await websocket.close()


@app.get("/generate-report")
async def generate_report():
    try:
        generate_trade_report(trades_file, output_dir)
        return {"message": "Trade report generated successfully."}
    except Exception as e:
        return {"error": f"Error generating report: {e}"}


@app.get("/reports/archive/{file_name}", response_class=HTMLResponse)
async def view_report(request: Request, file_name: str, symbol: str = "All", timeframe: str = "All", signal: str = "All"):
    """View a specific archived report with filters."""
    archive_dir = os.path.join(output_dir, "archive")
    file_path = os.path.join(archive_dir, file_name)
    
    if not os.path.exists(file_path):
        return HTMLResponse(content="Report not found", status_code=404)
    
    # Load trade data for filtering
    trades_df = pd.read_csv(trades_file) if os.path.exists(trades_file) else pd.DataFrame()
    
    # Apply filters
    filtered_trades = trades_df
    if symbol != "All":
        filtered_trades = filtered_trades[filtered_trades['symbol'] == symbol]
    if timeframe != "All":
        filtered_trades = filtered_trades[filtered_trades['timeframe'] == timeframe]
    if signal != "All":
        filtered_trades = filtered_trades[filtered_trades['type'] == signal]
    
    # Organize filtered trade data
    organized_trades = organize_trade_data(filtered_trades,symbol, timeframe, signal)
    
    # Generate filtered html report
    report_file = generate_html_report(organized_trades, output_dir,symbol, timeframe, signal)
    
    with open(os.path.join(output_dir, report_file), "r", encoding="utf-8") as f:
      content = f.read()

    return HTMLResponse(content=content)


@app.get("/archive", response_class=HTMLResponse)
async def view_archive(request: Request):
    archive_dir = os.path.join(output_dir, "archive")
    report_files = []
    if os.path.exists(archive_dir):
         report_files = [f for f in os.listdir(archive_dir) if f.startswith("trade_report_") and f.endswith(".html")]
    
    # Get unique symbols, timeframes, and signals
    all_trades_df = pd.read_csv(trades_file) if os.path.exists(trades_file) else pd.DataFrame()
    
    unique_symbols = ["All"] + sorted(all_trades_df['symbol'].unique().tolist()) if not all_trades_df.empty else ["All"]
    unique_timeframes = ["All"] + timeframes
    unique_signals = ["All"] + sorted(all_trades_df['type'].unique().tolist()) if not all_trades_df.empty else ["All"]

    return templates.TemplateResponse(
        "archive.html", 
        {
            "request": request, 
            "report_files": report_files,
            "symbols": unique_symbols,
            "timeframes": unique_timeframes,
            "signals": unique_signals
        }
    )
