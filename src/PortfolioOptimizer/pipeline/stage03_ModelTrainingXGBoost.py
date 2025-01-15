import os
import pandas as pd
from PortfolioOptimizer.logging import logger
from PortfolioOptimizer.utils.utils import read_yaml
from PortfolioOptimizer.components.modeltrainingXGBoost import XGBoostForecasting

def main():
    configs = read_yaml("config/config.yaml")
    processed_dir = configs['paths']['processed_dir']
    forecast_period = configs['forecast_period']
    symbols = configs['symbols']['currencies']

    for symbol in symbols:
        file_name = f"{symbol}_Featured.csv"
        file_path = os.path.join(processed_dir, file_name)

        if not os.path.exists(file_path):
            logger.warning(f"Processed data file not found for {symbol}: {file_path}")
            continue

        logger.info(f"Loading processed data for {symbol} from {file_path}")
        data = pd.read_csv(file_path)

        xgboost_forecasting = XGBoostForecasting(
            data=data,
            date_column='ds',
            target_column='y',
            config=configs,
        )

        logger.info(f"Preprocessing data for {symbol}.")
        xgboost_forecasting.preprocess_data()

        logger.info(f"Training XGBoost model for {symbol}.")
        xgboost_forecasting.train_model(training_period=730)

        logger.info(f"Forecasting future values for {symbol}.")
        forecast = xgboost_forecasting.forecast(future_periods=forecast_period)

        logger.info(f"Saving forecast results for {symbol}.")
        xgboost_forecasting.save_forecast(forecast, coin_name=symbol)

        # logger.info(f"Plotting forecast results for {symbol}.")
        # xgboost_forecasting.plot_forecast(forecast, coin_name=symbol)

if __name__ == "__main__":
    main()
