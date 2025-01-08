import os
import asyncio
from PortfolioOptimizer.components.dataingestion import DataIngestion
from PortfolioOptimizer.logging import logger
from PortfolioOptimizer.utils.utils import read_yaml
from dotenv import load_dotenv

load_dotenv()

configs = read_yaml("config/config.yaml")

STAGE_NAME = "Data Ingestion Stage"

class DataIngestionPipeline:
    def __init__(self):
        pass

    def main(self):
        COIN_MARKETCAP_API = os.getenv("COIN_MARKETCAP_API")
        print(f"<------------ {COIN_MARKETCAP_API} -------------->")
        data_ingestion = DataIngestion(api_key=COIN_MARKETCAP_API)
        asyncio.run(data_ingestion.fetch_last_year_daily())

if __name__ == "__main__":
    try:
        logger.info(f">>>>>> Stage {STAGE_NAME} started <<<<<<")
        obj = DataIngestionPipeline()
        obj.main()
        logger.info(f">>>>>> Stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e

