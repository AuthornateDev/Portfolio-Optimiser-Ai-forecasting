import pandas as pd
import requests
import datetime
import time
import os
from dotenv import load_dotenv


load_dotenv()

class BinanceIngestionData:
    def __init__(self, symbol, interval, start_date, end_date, output_dir):
        self.symbol = symbol
        self.interval = interval
        self.start_date = start_date
        self.end_date = end_date
        self.output_dir = output_dir
        self.base_url = "https://api.binance.com/api/v1/klines"
        self.api_key = os.getenv("BINANCE_API_KEY")  
        self.secret_key = os.getenv("BINANCE_SECRET_KEY")  
        self.max_retries = 5  
        self.retry_delay = 5  

        if not self.api_key or not self.secret_key:
            raise ValueError("API key and/or secret key not found in environment variables")

    def fetch_data(self):
        params = {
            "symbol": self.symbol,
            "interval": self.interval,
            "startTime": int(datetime.datetime.strptime(self.start_date, "%Y-%m-%d").timestamp() * 1000),
            "endTime": int(datetime.datetime.strptime(self.end_date, "%Y-%m-%d").timestamp() * 1000),
            "limit": 1000
        }

        headers = {
            "X-MBX-APIKEY": self.api_key  
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(self.base_url, params=params, headers=headers)
                data = response.json()

                if response.status_code == 200 and data:
                    return data
                else:
                    raise Exception(f"Error {response.status_code}: {response.text}")

            except Exception as e:
                print(f"Attempt {attempt}: Failed to fetch data for {self.symbol}. Error: {e}")
                if attempt < self.max_retries:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    raise Exception(f"Exceeded maximum retries for {self.symbol}.") from e

    def process_data(self, data):
        df = pd.DataFrame(data, columns=[
            "Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time", 
            "Quote Asset Volume", "Number of Trades", "Taker Buy Base Asset Volume", 
            "Taker Buy Quote Asset Volume", "Ignore"
        ])

        df["Open Time"] = pd.to_datetime(df["Open Time"], unit="ms")
        df.set_index("Open Time", inplace=True)
        df = df.astype({
            "Open": "float", 
            "High": "float", 
            "Low": "float", 
            "Close": "float", 
            "Volume": "float", 
            "Quote Asset Volume": "float", 
            "Number of Trades": "int", 
            "Taker Buy Base Asset Volume": "float", 
            "Taker Buy Quote Asset Volume": "float"
        })

        return df

    def save_to_csv(self, df):
        file_path = f"{self.output_dir}/{self.symbol}_2Y.csv"
        df.to_csv(file_path)
        print(f"Data for {self.symbol} saved to {file_path}")

