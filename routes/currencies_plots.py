import os
import pandas as pd
import io
import math
import numpy as np
import matplotlib.pyplot as plt
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from PortfolioOptimizer.utils.utils import read_yaml
from PortfolioOptimizer.components.modelforecasting import ModelForecasting
import plotly.graph_objects as go
from pydantic import BaseModel
from typing import List

router = APIRouter(tags=["Currencies Plots"])

config_path = "config/config.yaml"
config = read_yaml(config_path)
symbols = config['symbols']['currencies']
model_forecasting = ModelForecasting(config_path=config_path)

output_dir = "static"
os.makedirs(output_dir, exist_ok=True)

class CoinRequest(BaseModel):
    coins_names: List[str]

def generate_plot(symbol):
    """
    Generate a Plotly forecast plot for a given symbol.
    """
    try:
        historical_data, forecast_data = model_forecasting.load_data(symbol)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=historical_data['ds'], y=historical_data['y'], mode='lines', name='Historical Data', line=dict(color='black')))
        fig.add_trace(go.Scatter(x=forecast_data['ds'], y=forecast_data['yhat'], mode='lines', name='Forecast', line=dict(color='red', dash='dash')))

        fig.update_layout(
            title=f"{symbol} Forecasting",
            xaxis_title="Date",
            yaxis_title="Value",
            template="plotly_white",
            legend=dict(orientation="h", x=0.5, y=-0.2, xanchor="center"),
            height=600
        )
        return fig.to_html(full_html=False, include_plotlyjs=True)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Data files for {symbol} are missing!")

def generate_combined_matplotlib_plot(symbols):
    """
    Generate a combined plot with forecasts for multiple symbols.
    """
    try:
        n_plots = len(symbols)
        n_cols = min(2, n_plots)
        n_rows = math.ceil(n_plots / n_cols)
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15 * n_cols, 8 * n_rows))
        axes = axes.flatten() if n_plots > 1 else [axes]

        for idx, (symbol, ax) in enumerate(zip(symbols, axes)):
            historical_data, forecast_data = model_forecasting.load_data(symbol)
            forecast_start_date = forecast_data['ds'].iloc[0]
            today_date = pd.Timestamp.now().normalize()
            
            ax.plot(historical_data['ds'], historical_data['y'], label="Historical Data", color="black")
            ax.plot(forecast_data['ds'], forecast_data['yhat'], label="Forecast", color="red", linestyle="--")
            ax.axvline(forecast_start_date, color="blue", linestyle="--", label="Forecast Start")
            
            if today_date in historical_data['ds'].values:
                current_value = historical_data.loc[historical_data['ds'] == today_date, 'y'].values[0]
                ax.scatter(today_date, current_value, color="green", label=f"Today's Value: {current_value:.2f}")
            
            ax.set_title(f"{symbol} Forecasting", fontsize=12)
            ax.legend(fontsize=10)
            ax.grid(True)

        for idx in range(len(symbols), len(axes)):
            axes[idx].set_visible(False)

        plt.tight_layout()
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=150)
        buffer.seek(0)
        plt.close()
        return buffer
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Data files are missing: {str(e)}")

@router.get("/CoinsForecasting")
async def get_forecast(currencies: str = Query(...), display: bool = Query(False)):
    """
    Generate and return forecast plots for selected currencies.
    """
    selected_currencies = currencies.split(",")
    invalid_currencies = [sym for sym in selected_currencies if sym not in symbols]

    if invalid_currencies:
        raise HTTPException(status_code=400, detail=f"Invalid symbols: {', '.join(invalid_currencies)}")

    plots = [f"<h2>{symbol}</h2>{generate_plot(symbol)}" for symbol in selected_currencies]
    unique_filename = f"forecast_{'_'.join(selected_currencies)}.html"
    file_path = os.path.join(output_dir, unique_filename)

    html_template = f"<html><body>{''.join(plots)}</body></html>"
    with open(file_path, "w") as f:
        f.write(html_template)

    if display:
        return RedirectResponse(url=f"/static/{unique_filename}")
    return JSONResponse(content={"url": f"/static/{unique_filename}"})

@router.get("/CoinForecastingSubPlots")
async def get_combined_forecast(symbols: List[str] = Query(...)):
    """
    Generate a combined Matplotlib plot for multiple currencies.
    """
    invalid_symbols = [sym for sym in symbols if sym not in config['symbols']['currencies']]
    if invalid_symbols:
        raise HTTPException(status_code=400, detail=f"Invalid symbols: {', '.join(invalid_symbols)}")

    buffer = generate_combined_matplotlib_plot(symbols)
    return StreamingResponse(buffer, media_type="image/png", headers={"Content-Disposition": "inline; filename=combined_forecast.png"})

@router.post("/CoinForecastingPlots")
async def generate_individual_forecasts(request: CoinRequest):
    """
    Generate individual forecast plots for multiple currencies.
    """
    invalid_symbols = [sym for sym in request.coins_names if sym not in symbols]
    if invalid_symbols:
        raise HTTPException(status_code=400, detail=f"Invalid symbols: {', '.join(invalid_symbols)}")

    plots_dir = os.path.join(output_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)
    plot_urls = []

    for symbol in request.coins_names:
        buffer = generate_combined_matplotlib_plot([symbol])
        filename = f"{symbol}_forecast.png"
        file_path = os.path.join(plots_dir, filename)

        with open(file_path, "wb") as f:
            f.write(buffer.getvalue())
        plot_urls.append(f"/static/plots/{filename}")

    return JSONResponse(content={"status": "success", "plots": plot_urls})
