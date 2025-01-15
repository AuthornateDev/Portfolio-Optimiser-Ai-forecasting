import os
import xgboost as xgb
import pandas as pd
from datetime import timedelta
from PortfolioOptimizer.logging import logger
from PortfolioOptimizer.utils.utils import read_yaml
import plotly.graph_objects as go


class XGBoostForecasting:
    def __init__(self, data, date_column, target_column, config):
        """
        Initialize the XGBoostForecasting class.

        Parameters:
        - data: DataFrame containing the data.
        - date_column: Name of the column containing the dates.
        - target_column: Name of the column to forecast.
        - config: Dictionary with configuration details.
        """
        self.data = data
        self.date_column = date_column
        self.target_column = target_column
        self.config = config

    def preprocess_data(self):
        """Preprocess the data to prepare it for the XGBoost model."""
        self.data = self.data.rename(columns={self.date_column: 'ds', self.target_column: 'y'})
        self.data['ds'] = pd.to_datetime(self.data['ds'])
        self.data['day'] = self.data['ds'].dt.day
        self.data['month'] = self.data['ds'].dt.month
        self.data['weekday'] = self.data['ds'].dt.weekday

    def prepare_features(self, training_period=730):
        """Prepare features for the model."""
        last_date = self.data['ds'].max()
        start_date = last_date - timedelta(days=training_period)
        training_data = self.data[self.data['ds'] >= start_date]
        features = training_data[['day', 'month', 'weekday']]
        target = training_data['y']
        return features, target, training_data

    def train_model(self, training_period=730):
        """Train the XGBoost model using the last `training_period` days."""
        features, target, _ = self.prepare_features(training_period)
        self.model = xgb.XGBRegressor(
            objective='reg:squarederror', n_estimators=1000,
            learning_rate=0.01, max_depth=6,
            subsample=0.8, colsample_bytree=0.8
        )
        self.model.fit(features, target)

    def forecast(self, future_periods=180):
        """Forecast future data using XGBoost."""
        last_date = self.data['ds'].max()
        forecast_dates = [last_date + timedelta(days=i) for i in range(1, future_periods + 1)]
        future_features = pd.DataFrame({
            'day': [d.day for d in forecast_dates],
            'month': [d.month for d in forecast_dates],
            'weekday': [d.weekday() for d in forecast_dates]
        })
        forecast_values = self.model.predict(future_features)
        last_training_value = self.data['y'].iloc[-1]
        first_forecast_value = forecast_values[0]
        adjustment_factor = last_training_value - first_forecast_value
        forecast_values += adjustment_factor

        return pd.DataFrame({'ds': forecast_dates, 'yhat': forecast_values})


    def save_forecast(self, forecast, coin_name):
        """Save the forecast results to a specified directory."""
        forecast_dir = self.config['paths']['foresast_dir']
        os.makedirs(forecast_dir, exist_ok=True)
        forecast_path = os.path.join(forecast_dir, f"{coin_name}_Forecast.csv")
        forecast.to_csv(forecast_path, index=False)
        logger.info(f"Forecast saved at: {forecast_path}")

    def plot_forecast(self, forecast, coin_name):
        """Plot the forecast results."""
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self.data['ds'], y=self.data['y'], mode='lines', name='Actual', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast', line=dict(color='green')))
        fig.update_layout(title=f'Forecast for {coin_name}', xaxis_title='Date', yaxis_title='Value', template='plotly_dark')
        fig.show()
