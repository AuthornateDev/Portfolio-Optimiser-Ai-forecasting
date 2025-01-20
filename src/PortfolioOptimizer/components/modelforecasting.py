import os
import pandas as pd
import plotly.graph_objects as go
from PortfolioOptimizer.logging import logger
from PortfolioOptimizer.utils.utils import read_yaml
from datetime import timedelta

class ModelForecasting:
    def __init__(self, config_path):
        """
        Initialize the ModelForecasting class.
        Parameters:
        - config_path: Path to the configuration YAML file.
        """
        self.config = read_yaml(config_path)
        self.processed_dir = self.config['paths']['processed_dir']
        self.forecast_dir = self.config['paths']['foresast_dir']
        self.forecast_period = self.config['forecast_period']
        self.symbols = self.config['symbols']['currencies']
    def load_data(self, symbol):
        """
        Load processed and forecast data for a given symbol.
        Parameters:
        - symbol: The coin symbol to load data for.
        Returns:
        - historical_data: DataFrame containing the last 6 months of processed data.
        - forecast_data: DataFrame containing the forecast results.
        """
        processed_file = os.path.join(self.processed_dir, f"{symbol}_Featured.csv")
        forecast_file = os.path.join(self.forecast_dir, f"{symbol}_Forecast.csv")
        if not os.path.exists(processed_file) or not os.path.exists(forecast_file):
            raise FileNotFoundError(f"Data files for {symbol} are missing!")
        historical_data = pd.read_csv(processed_file)
        forecast_data = pd.read_csv(forecast_file)
        historical_data['ds'] = pd.to_datetime(historical_data['ds'])
        forecast_data['ds'] = pd.to_datetime(forecast_data['ds'])
        last_date = historical_data['ds'].max()
        start_date = last_date - timedelta(days=180)
        historical_data = historical_data[historical_data['ds'] >= start_date]
        return historical_data, forecast_data
    def plot_forecast(self, symbol):
        """
        Plot forecast results alongside historical data for a given symbol.
        Parameters:
        - symbol: The coin symbol to plot data for.
        """
        historical_data, forecast_data = self.load_data(symbol)
        fig = go.Figure()
        # Historical data
        fig.add_trace(go.Scatter(
            x=historical_data['ds'], 
            y=historical_data['y'], 
            mode='lines', 
            name='Historical Data', 
            line=dict(color='blue')
        ))
        # Forecast data
        fig.add_trace(go.Scatter(
            x=forecast_data['ds'], 
            y=forecast_data['yhat'], 
            mode='lines', 
            name='Forecast', 
            line=dict(color='green', dash='dash')
        ))
        # Layout updates
        fig.update_layout(
            title=f"{symbol} Forecast vs Historical Data",
            xaxis_title="Date",
            yaxis_title="Value",
            template="plotly_dark",
            legend=dict(orientation="h", x=0.5, y=-0.2, xanchor="center"),
            height=600
        )
        logger.info(f"Plotting forecast for {symbol}.")
        fig.show()