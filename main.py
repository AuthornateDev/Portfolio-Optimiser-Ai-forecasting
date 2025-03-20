from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routes import currencies_plots, seaborn_plots
import subprocess
import os
from pydantic import BaseModel

app = FastAPI(
    title="Currency Forecast API",
    description="An API to generate and display forecast plots for selected currencies using Plotly.",
    version="1.0.0",
)

# Add the CORSMiddleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
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


class PipelineResponse(BaseModel):
    success: bool
    message: str

@app.post("/run_pipeline", response_model=PipelineResponse)
async def run_pipeline():
    """
    Runs a specified Python pipeline file and checks for success.
    """
    pipeline_file = "src/PortfolioOptimizer/pipeline/pipeline.py"  # Replace with your pipeline file name
    try:
        # Check if the file exists
        if not os.path.exists(pipeline_file):
            raise FileNotFoundError(f"Pipeline file '{pipeline_file}' not found.")

        # Run the pipeline file using subprocess
        process = subprocess.run(
            ["python", pipeline_file],
            capture_output=True,
            text=True,
            check=True,  # Raise CalledProcessError for non-zero exit codes
        )

        return PipelineResponse(success=True, message="Pipeline executed successfully.")

    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except subprocess.CalledProcessError as e:
        # Pipeline execution failed
        error_message = f"Pipeline execution failed with exit code {e.returncode}. Output: {e.stderr}"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message)

    except Exception as e:
        # Other unexpected errors
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
