import os
from PortfolioOptimizer.logging import logger
from PortfolioOptimizer.utils.utils import read_yaml
from PortfolioOptimizer.pipeline.stage01_DataIngestion_Binance import DataIngestionBinancePipeline
from PortfolioOptimizer.pipeline.stage02_DataProcessing import DataProcessingPipeline
from PortfolioOptimizer.pipeline.stage03_ModelTrainingXGBoost import main as model_training_main
from PortfolioOptimizer.pipeline.stage04_ModelForecasting import main as model_forecasting_main
from dotenv import load_dotenv

load_dotenv()

def main():
    logger.info("Reading configuration for the pipeline.")
    config_path = "config/config.yaml"
    config = read_yaml(config_path)

    try:
        # Stage 01: Data Ingestion
        logger.info(">>>>>>>>>>>>> Starting Stage 01: Data Ingestion 🫠 <<<<<<<<<<<<< ")
        data_ingestion_pipeline = DataIngestionBinancePipeline(config)
        data_ingestion_pipeline.main()
        logger.info(">>>>>>>>>>>>> Completed Stage 01: Data Ingestion 👍 <<<<<<<<<<<<< \n\n")

        # Stage 02: Data Processing
        logger.info(">>>>>>>>>>>>> Starting Stage 02: Data Processing 🫠 <<<<<<<<<<<<< ")
        data_processing_pipeline = DataProcessingPipeline()
        data_processing_pipeline.main()
        logger.info(">>>>>>>>>>>>> Completed Stage 02: Data Processing 👍 <<<<<<<<<<<<< \n\n")

        # Stage 03: Model Training and Forecasting
        logger.info(">>>>>>>>>>>>> Starting Stage 03: Model Training 🫠 <<<<<<<<<<<<< ")
        model_training_main()
        logger.info(">>>>>>>>>>>>> Completed Stage 03: Model Training 👍 <<<<<<<<<<<<< \n\n")

        # Stage 04: Model Forecasting and Visualization
        logger.info(">>>>>>>>>>>>> Starting Stage 04: Model Forecasting 🫠 <<<<<<<<<<<<< ")
        model_forecasting_main()
        logger.info(">>>>>>>>>>>>> Completed Stage 04: Model Forecasting 👍 <<<<<<<<<<<<< \n\n")

    except Exception as e:
        logger.exception(f"Pipeline execution failed: {e}")
        raise e


if __name__ == "__main__":
    logger.info("Starting the PortfolioOptimizer Pipeline.")
    main()
    logger.info("Completed the PortfolioOptimizer Pipeline.")
