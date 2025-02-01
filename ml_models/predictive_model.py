# D:\Adnan_project\TradingBot\ml_models\predictive_model.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
import joblib
import os
from indicator_calculator import calculate_indicators  # Import indicators

MODEL_PATH = "D:\\Adnan_project\\TradingBot\\ml_models\\trained_model.joblib"

def load_historical_data(file_path):
    try:
      df = pd.read_csv(file_path)
      if df.empty:
          print(f"Error: No data found at {file_path}")
          return None
      df['timestamp'] = pd.to_datetime(df['timestamp'])
      df = df.sort_values(by='timestamp')
      return df
    except Exception as e:
        print(f"Error loading historical data : {e}")
        return None

def prepare_data(df: pd.DataFrame, target_column: str):
    """Prepares the data for model training"""
    
    # Add your data processing logic here
    df = calculate_indicators(df)

    if 'close' not in df.columns or df.empty:
       print("Error: 'close' column not found in data.")
       return None, None, None, None
    
    df['price_change'] = df['close'].diff()
    df['price_change'] = df['price_change'].fillna(0)
    
    df['target'] = df['price_change'].apply(lambda x: 1 if x > 0 else 0)
    df = df.dropna()

    if df.empty:
         print("Error: dataframe is empty")
         return None, None, None, None
    
    X = df.drop(columns=[target_column, 'price_change', 'open', 'high', 'low', 'volume', 'close_time', 'quote_asset_volume', 'num_trades', 'taker_buy_base', 'taker_buy_quote','ignore'])
    y = df[target_column]
    
    if X.empty or y.empty:
       print("Error: features or target are empty")
       return None, None, None, None
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # scale data
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    return X_train, X_test, y_train, y_test, scaler

def train_model(X_train, y_train):
    """Trains the model"""
    model = LogisticRegression()
    model.fit(X_train, y_train)
    
    if not os.path.exists(os.path.dirname(MODEL_PATH)):
        os.makedirs(os.path.dirname(MODEL_PATH))
    joblib.dump(model, MODEL_PATH)
    return model

def validate_model(model, X_test, y_test):
    """Validates the model"""
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    return accuracy

def inference(model, input_data, scaler):
      """Runs the inference"""
      input_data = calculate_indicators(input_data)
      if 'close' not in input_data.columns or input_data.empty:
          print("Error 'close' column not found in data")
          return None
      
      input_data = input_data.drop(columns=[ 'open', 'high', 'low', 'volume', 'close_time', 'quote_asset_volume', 'num_trades', 'taker_buy_base', 'taker_buy_quote','ignore'])
      
      scaled_input_data = scaler.transform(input_data)
      prediction = model.predict(scaled_input_data)
      return prediction
    
def load_model():
    try:
       model = joblib.load(MODEL_PATH)
       return model
    except Exception as e:
        print(f"Error loading model {e}")
        return None
