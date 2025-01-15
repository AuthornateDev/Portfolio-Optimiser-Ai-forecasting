import os
from PortfolioOptimizer.components.dataprocessing import DataProcessing
from PortfolioOptimizer.logging import logger
from PortfolioOptimizer.utils.utils import read_yaml
from dotenv import load_dotenv
import warnings

warnings.filterwarnings("ignore")
load_dotenv()

configs = read_yaml("config/config.yaml")
STAGE_NAME = "Data Processing Stage"


class DataProcessingPipeline:
    def __init__(self):
        self.artifacts_dir = configs["paths"]["artifacts_dir"]
        self.processed_dir = configs["paths"]["processed_dir"]
        self.symbols = configs["symbols"]["currencies"]

        os.makedirs(self.processed_dir, exist_ok=True)

    def process_csv(self, csv_path, output_path):
        data_processor = DataProcessing(csv_path)
        final_df = data_processor.process_data()
        final_df.to_csv(output_path, index=False)
        logger.info(f"Processed and saved: {output_path}")

    def main(self):
        for symbol in self.symbols:
            symbol_file = os.path.join(self.artifacts_dir, f"{symbol}_2Y.csv")
            output_file = os.path.join(self.processed_dir, f"{symbol}_Featured.csv")

            if os.path.exists(symbol_file):
                self.process_csv(symbol_file, output_file)
            else:
                logger.warning(f"File not found: {symbol_file}")


if __name__ == "__main__":
    try:
        logger.info(f">>>>>> Stage {STAGE_NAME} Started <<<<<<")
        pipeline = DataProcessingPipeline()
        pipeline.main()
        logger.info(f">>>>>> Stage {STAGE_NAME} Completed <<<<<<\n\n")
    except Exception as e:
        logger.exception(e)
        raise e
