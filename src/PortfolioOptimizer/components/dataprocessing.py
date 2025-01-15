import pandas as pd
from prophet import Prophet
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings

warnings.filterwarnings("ignore")


class DataProcessing:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.df = pd.read_csv(self.csv_path, parse_dates=["Open Time"])

    def add_features(self):
        self.df = self.df.rename(columns={"Open Time": "ds", "Close": "y"})
        self.df = self.df.drop(columns=["Ignore"], errors='ignore')
        self.df['High_Low_Diff'] = self.df['High'] - self.df['Low']
        self.df['Open_Close_Diff'] = self.df['Open'] - self.df['y']
        self.df['Average_Price'] = (self.df['High'] + self.df['Low'] + self.df['y']) / 3
        self.df['Volume_Weighted_Price'] = self.df['Quote Asset Volume'] / self.df['Volume']

    def generate_prophet_features(self):
        prophet_model = Prophet(
            growth='linear',
            seasonality_mode='additive',
            interval_width=0.95,
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=False
        )
        prophet_model.fit(self.df[['ds', 'y']])
        prophet_results = prophet_model.predict(self.df[['ds']])
        return prophet_results

    def generate_ets_features(self):
        self.df['Triple_Multiplicative_ETS'] = ExponentialSmoothing(
            self.df['y'], trend='mul', seasonal='mul', seasonal_periods=24 * 7
        ).fit().fittedvalues

        self.df['Triple_Additive_ETS'] = ExponentialSmoothing(
            self.df['y'], trend='add', seasonal='add', seasonal_periods=24 * 7
        ).fit().fittedvalues

    def process_data(self):
        self.add_features()
        prophet_results = self.generate_prophet_features()
        self.generate_ets_features()
        # Merge Prophet results with the original dataframe
        prophet_results['ds'] = prophet_results['ds'].astype(str)
        self.df['ds'] = self.df['ds'].astype(str)
        featured_df = pd.merge(self.df, prophet_results, how='left', on='ds')
        return featured_df
