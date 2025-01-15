import pandas as pd
import requests
import datetime

class BinanceIngestionData:
    def __init__(self, symbol, interval, start_date, end_date, output_dir):
        self.symbol = symbol
        self.interval = interval
        self.start_date = start_date
        self.end_date = end_date
        self.output_dir = output_dir
        self.base_url = "https://api.binance.com/api/v3/klines"

    def fetch_data(self):
        params = {
            "symbol": self.symbol,
            "interval": self.interval,
            "startTime": int(datetime.datetime.strptime(self.start_date, "%Y-%m-%d").timestamp() * 1000),
            "endTime": int(datetime.datetime.strptime(self.end_date, "%Y-%m-%d").timestamp() * 1000),
            "limit": 1000
        }
        response = requests.get(self.base_url, params=params)
        data = response.json()

        if response.status_code != 200 or not data:
            raise Exception(f"Failed to fetch data for {self.symbol}. Check your symbol, interval, or date range.")

        return data

    def process_data(self, data):
        df = pd.DataFrame(data, columns=[
            "Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time", 
            "Quote Asset Volume", "Number of Trades", "Taker Buy Base Asset Volume", 
            "Taker Buy Quote Asset Volume", "Ignore"
        ])

        # Convert to proper data types
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
