import os
from datetime import datetime, timedelta
from PortfolioOptimizer.components.dataingestion_binance import BinanceIngestionData
from PortfolioOptimizer.logging import logger
from PortfolioOptimizer.utils.utils import read_yaml
from dotenv import load_dotenv

load_dotenv()

configs = read_yaml("config/config.yaml")

STAGE_NAME = "Data Ingestion Stage"

class DataIngestionBinancePipeline:
    def __init__(self, config):
        self.config = config

    def main(self):
        symbols = self.config["symbols"]["currencies"]
        interval = "1d"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")
        output_dir = self.config["paths"]["artifacts_dir"]

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for symbol in symbols:
            try:
                binance_data = BinanceIngestionData(symbol, interval, start_date, end_date, output_dir)
                raw_data = binance_data.fetch_data()
                processed_data = binance_data.process_data(raw_data)
                binance_data.save_to_csv(processed_data)
                logger.info(f"Successfully processed data for {symbol}")
            except Exception as e:
                logger.error(f"Error processing data for {symbol}: {e}")

if __name__ == "__main__":
    try:
        logger.info(f">>>>>> Stage {STAGE_NAME} Started <<<<<<")
        pipeline = DataIngestionBinancePipeline(configs)
        pipeline.main()
        logger.info(f">>>>>> Stage {STAGE_NAME} Completed <<<<<<\n\n")
    except Exception as e:
        logger.exception(e)
        raise e
