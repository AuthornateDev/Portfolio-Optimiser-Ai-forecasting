import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import currencies_plots, seaborn_plots

app = FastAPI(
    title="Currency Forecast API",
    description="An API to generate and display forecast plots for selected currencies using Plotly.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(currencies_plots.router)
app.include_router(seaborn_plots.router)

@app.get("/")
async def root():
    """
    Root endpoint to display a welcome message.
    """
    return {
        "message": "Welcome to the Currency Forecast API! Visit /docs for API documentation."
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000)) 
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
