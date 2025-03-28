import os
import pandas as pd
import io
import matplotlib.pyplot as plt
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from PortfolioOptimizer.utils.utils import read_yaml
from PortfolioOptimizer.components.modelforecasting import ModelForecasting
import plotly.graph_objects as go

router = APIRouter(tags=["Currencies Plots"])

config_path = "config/config.yaml"
config = read_yaml(config_path)
symbols = config['symbols']['currencies']
model_forecasting = ModelForecasting(config_path=config_path)

output_dir = "static"
os.makedirs(output_dir, exist_ok=True)

def generate_plot(symbol):
    """
    Generate a Plotly forecast plot for a given symbol.
    """
    try:
        historical_data, forecast_data = model_forecasting.load_data(symbol)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=historical_data['ds'], 
            y=historical_data['y'], 
            mode='lines', 
            name='Historical Data', 
            line=dict(color='black')
        ))

        fig.add_trace(go.Scatter(
            x=forecast_data['ds'], 
            y=forecast_data['yhat'], 
            mode='lines', 
            name='Forecast', 
            line=dict(color='red', dash='dash')
        ))

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
    

def generate_matplotlib_plot(symbol):
    """
    Generate an enhanced Matplotlib forecast plot for a given symbol.
    """
    try:
        historical_data, forecast_data = model_forecasting.load_data(symbol)
        
        forecast_start_date = forecast_data['ds'].iloc[0]
        today_date = pd.Timestamp.now().normalize()
        
        current_value = None
        if today_date in historical_data['ds'].values:
            current_value = historical_data.loc[historical_data['ds'] == today_date, 'y'].values[0]
        
        plt.figure(figsize=(16, 9))
        plt.plot(historical_data['ds'], historical_data['y'], label="Historical Data", color="black", linewidth=2)
        plt.plot(forecast_data['ds'], forecast_data['yhat'], label="Forecast", color="red", linestyle="--", linewidth=2)
        
        plt.axvline(forecast_start_date, color="blue", linestyle="--", linewidth=1.5, label="Forecast Start")
        
        if current_value is not None:
            plt.scatter(today_date, current_value, color="green", label=f"Today's Value: {current_value:.2f}", zorder=5)
            plt.text(
                today_date, current_value, f" {current_value:.2f}",
                color="green", fontsize=10, fontweight="bold", verticalalignment="bottom"
            )

        plt.title(f"{symbol} Forecasting with Highlights", fontsize=18, fontweight="bold")
        plt.xlabel("Date", fontsize=14)
        plt.ylabel("Value", fontsize=14)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.legend(fontsize=12)
        plt.grid(True, linestyle="--", alpha=0.6)
        
        buffer = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format="png", dpi=150)
        buffer.seek(0)
        plt.close()

        return buffer
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Data files for {symbol} are missing!")



@router.get("/CoinsForecasting")
async def get_forecast(currencies: str = Query(..., description="Comma-separated list of currency symbols"), display: bool = Query(False, description="Whether to display the plots directly")):
    selected_currencies = currencies.split(",")
    invalid_currencies = [sym for sym in selected_currencies if sym not in symbols]

    if invalid_currencies:
        raise HTTPException(status_code=400, detail=f"Invalid symbols: {', '.join(invalid_currencies)}")

    plots = []
    for symbol in selected_currencies:
        plot_html = generate_plot(symbol)
        plots.append(f"<h2>{symbol}</h2>{plot_html}")

    unique_filename = f"forecast_{'_'.join(selected_currencies)}.html"
    static_dir = "static"
    os.makedirs(static_dir, exist_ok=True)
    file_path = os.path.join(static_dir, unique_filename)

    html_template = """
    <html>
        <head>
            <title>Forecast Results</title>
            <style>
                body {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    font-family: Arial, sans-serif;
                }}
                h1 {{
                    color: #333;
                    text-align: center;
                }}
                h2 {{
                    color: #666;
                    margin-top: 30px;
                }}
                .plot-container {{
                    margin-bottom: 40px;
                }}
            </style>
        </head>
        <body>
            <h1>Forecast Results</h1>
            <div class="plot-container">
                {0}
            </div>
        </body>
    </html>
    """

    combined_html = html_template.format("".join(plots))

    with open(file_path, "w") as f:
        f.write(combined_html)

    if display:
        return RedirectResponse(url=f"/static/{unique_filename}")
    return JSONResponse(content={"url": f"/static/{unique_filename}"})

@router.get("/display/{filename}", response_class=HTMLResponse)
async def display_plots(filename: str):
    file_path = os.path.join("static", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Plot file not found")
    
    with open(file_path, "r") as f:
        content = f.read()
    return HTMLResponse(content=content)

@router.get("/CoinForecastingPlots")
async def get_forecast_enhanced(
    currencies: list[str] = Query(..., description="List of currency symbols (e.g., ETHUSDT,BTCUSDT)")
):
    """
    Generate and return Matplotlib forecast plots for multiple currencies.
    """
    invalid_currencies = [sym for sym in currencies if sym not in symbols]

    if invalid_currencies:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid symbols: {', '.join(invalid_currencies)}"
        )

    buffers = {}
    for symbol in currencies:
        buffer = generate_matplotlib_plot(symbol)
        buffers[symbol] = buffer

    # Save plots and prepare response
    plots_dir = "static/plots"
    os.makedirs(plots_dir, exist_ok=True)
    plot_files = []
    for symbol, buffer in buffers.items():
        filename = f"{symbol}_forecast.png"
        file_path = os.path.join(plots_dir, filename)
        with open(file_path, "wb") as f:
            f.write(buffer.getvalue())
        plot_files.append(f"/{plots_dir}/{filename}")

    return JSONResponse(content={"plots": plot_files})