import io
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from PortfolioOptimizer.utils.utils import read_yaml
from PortfolioOptimizer.components.modelforecasting import ModelForecasting
from typing import List

router = APIRouter(tags=["Seaborn Plots"])

config_path = "config/config.yaml"
config = read_yaml(config_path)
symbols = config['symbols']['currencies']
model_forecasting = ModelForecasting(config_path=config_path)

@router.get("/SeabornForecastPlot")
async def get_seaborn_forecast_plot(symbol: str = Query(...)):
    """
    Generate and return a Seaborn forecast plot for a given symbol.
    """
    if symbol not in symbols:
        raise HTTPException(status_code=400, detail=f"Invalid symbol: {symbol}")

    try:
        historical_data, forecast_data = model_forecasting.load_data(symbol)

        historical_data['Type'] = 'Actual Data'
        forecast_data['Type'] = 'Forecasting'

        # Use pd.concat instead of append
        combined_data = pd.concat([
            historical_data[['ds', 'y', 'Type']],
            forecast_data[['ds', 'yhat']].rename(columns={'yhat': 'y'}).assign(Type='Forecast')
        ], ignore_index=True)

        plt.figure(figsize=(12, 6))
        sns.lineplot(data=combined_data, x='ds', y='y', hue='Type', style='Type', markers=False, dashes=False)
        plt.title(f"{symbol} Forecasting", fontsize=16)
        plt.xlabel("Date", fontsize=14)
        plt.ylabel("Value", fontsize=14)
        plt.legend(title="Data Type", loc='upper left')
        plt.grid(True)

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=150)
        buffer.seek(0)
        plt.close()

        return StreamingResponse(buffer, media_type="image/png", headers={"Content-Disposition": "inline; filename=forecast_plot.png"})
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Data files for {symbol} are missing!")
