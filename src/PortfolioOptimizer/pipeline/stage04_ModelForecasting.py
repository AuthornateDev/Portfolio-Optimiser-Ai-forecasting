from PortfolioOptimizer.logging import logger
from PortfolioOptimizer.utils.utils import read_yaml
from PortfolioOptimizer.components.modelforecasting import ModelForecasting

def main():
    logger.info("Reading configuration for Model Forecasting.")
    config_path = "config/config.yaml"
    config = read_yaml(config_path)

    model_forecasting = ModelForecasting(config_path=config_path)

    symbols = config['symbols']['currencies']
    for symbol in symbols:
        logger.info(f"Generating forecast plot for {symbol}.")
        try:
            model_forecasting.plot_forecast(symbol)
        except FileNotFoundError as e:
            logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()
