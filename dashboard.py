import os
import dash
from dash import dcc, html
import pandas as pd
import plotly.graph_objects as go
from PortfolioOptimizer.utils.utils import read_yaml
from PortfolioOptimizer.components.modelforecasting import ModelForecasting

config_path = "config/config.yaml"
config = read_yaml(config_path)
symbols = config['symbols']['currencies']

model_forecasting = ModelForecasting(config_path=config_path)

app = dash.Dash(__name__)
app.title = "Coin & Token Forecast Dashboard"

def generate_plot(symbol):
    try:
        historical_data, forecast_data = model_forecasting.load_data(symbol)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=historical_data['ds'], 
            y=historical_data['y'], 
            mode='lines', 
            name='Historical Data', 
            line=dict(color='blue')
        ))

        fig.add_trace(go.Scatter(
            x=forecast_data['ds'], 
            y=forecast_data['yhat'], 
            mode='lines', 
            name='Forecast', 
            line=dict(color='green', dash='dash')
        ))

        fig.update_layout(
            title=f"{symbol} Forecast vs Historical Data",
            xaxis_title="Date",
            yaxis_title="Value",
            template="plotly_dark",
            legend=dict(orientation="h", x=0.5, y=-0.2, xanchor="center"),
            height=600
        )
        return fig
    except FileNotFoundError as e:
        return f"Error loading data for {symbol}: {e}"

app.layout = html.Div([
    html.H1("Coin & Token Forecast Dashboard", style={'text-align': 'center'}),
    html.Div([
        dcc.Graph(
            id=f"plot-{symbol}",
            figure=generate_plot(symbol)
        ) for symbol in symbols
    ])
])

if __name__ == "__main__":
    app.run_server(debug=True)
