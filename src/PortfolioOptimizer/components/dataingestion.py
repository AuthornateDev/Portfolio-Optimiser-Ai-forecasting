import os
import aiohttp
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from PortfolioOptimizer.utils.utils import read_yaml
from PortfolioOptimizer.logging import logger
from dotenv import load_dotenv

load_dotenv()

configs = read_yaml("config/config.yaml")

class DataIngestion:
    def __init__(self, api_key: str, symbols: list = None, artifacts_dir: str = None):
        self.api_key = api_key
        self.symbols = symbols or configs["symbols"]["currencies"]
        self.artifacts_dir = artifacts_dir or configs["paths"]["artifacts_dir"]
        os.makedirs(self.artifacts_dir, exist_ok=True)

    async def fetch_data_batch(self, session, url, headers, params, retries=3):
        """
        Fetches data for a batch of cryptocurrencies asynchronously with retries.
        """
        for attempt in range(retries):
            try:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:
                        logger.warning("Rate limit hit. Waiting before retrying...")
                        await asyncio.sleep(10)
                    else:
                        logger.error(f"Failed to fetch: HTTP {response.status}")
                        return None
            except Exception as e:
                logger.error(f"Error fetching data: {str(e)}")
                await asyncio.sleep(5)
        return None

    async def fetch_crypto_data_async(self):
        """
        Fetches cryptocurrency data for multiple symbols asynchronously.
        """
        base_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {
            'X-CMC_PRO_API_KEY': self.api_key,
            'Accept': 'application/json'
        }

        batch_size = 10
        symbol_batches = [self.symbols[i:i + batch_size] for i in range(0, len(self.symbols), batch_size)]
        tasks = []

        async with aiohttp.ClientSession() as session:
            for batch in symbol_batches:
                params = {
                    'symbol': ','.join(batch),
                    'convert': 'USD'
                }
                tasks.append(self.fetch_data_batch(session, base_url, headers, params))

            responses = await asyncio.gather(*tasks)

        all_data = []
        for response in responses:
            if response:
                try:
                    for symbol, coin_data in response['data'].items():
                        quote_data = coin_data['quote']['USD']
                        record = {
                            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'symbol': symbol,
                            'price': quote_data['price'],
                            'volume_24h': quote_data['volume_24h'],
                            'volume_change_24h': quote_data['volume_change_24h'],
                            'percent_change_1h': quote_data['percent_change_1h'],
                            'percent_change_24h': quote_data['percent_change_24h'],
                            'percent_change_7d': quote_data['percent_change_7d'],
                            'percent_change_30d': quote_data['percent_change_30d'],
                            'percent_change_60d': quote_data['percent_change_60d'],
                            'percent_change_90d': quote_data['percent_change_90d'],
                            'market_cap': quote_data['market_cap'],
                            'market_cap_dominance': quote_data['market_cap_dominance'],
                            'fully_diluted_market_cap': quote_data['fully_diluted_market_cap'],
                            'circulating_supply': coin_data.get('circulating_supply'),
                            'total_supply': coin_data.get('total_supply')
                        }
                        all_data.append(record)
                except KeyError as e:
                    logger.error(f"Error processing response: {e}")

        return pd.DataFrame(all_data)

    async def fetch_last_year_daily(self):
        """
        Fetches cryptocurrency data for the last year, capturing daily details.
        Saves the data into a single CSV file in the artifacts directory.
        """
        aggregated_data = []
        current_time = datetime.now()
        start_time = current_time - timedelta(days=1050)

        while current_time > start_time:
            logger.info(f"Fetching data for {current_time.strftime('%Y-%m-%d')}...")
            df = await self.fetch_crypto_data_async()
            if not df.empty:
                df['date'] = current_time.strftime('%Y-%m-%d')
                aggregated_data.append(df)
            else:
                logger.warning("No data fetched for this day.")

            current_time -= timedelta(days=1)
            await asyncio.sleep(1)  

        if aggregated_data:
            final_df = pd.concat(aggregated_data, ignore_index=True)
            final_df.sort_values(by='date', inplace=True)
            filename = os.path.join(
                self.artifacts_dir, f"df_last_year_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            final_df.to_csv(filename, index=False)
            logger.info(f"Saved all data to {filename}")
        else:
            logger.warning("No data available for the last year.")