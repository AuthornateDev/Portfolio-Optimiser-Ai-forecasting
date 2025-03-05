PortfolioOptimizer
GitPat=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

# Please use python 3.10 version to avoid missing or unsupported dependencies

# CryptoPortfolioAI

CryptoPortfolioAI is a cryptocurrency forecasting and visualization pipeline. The project includes a data pipeline for forecasting crypto prices and a FastAPI server to display the resulting plots.

## Setup and Usage

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/CryptoPortfolioAI.git
cd CryptoPortfolioAI
```

### 2. Install Dependencies

If running locally, create a virtual environment and install dependencies:

```sh
python3 -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
pip install -r requirements.txt
```

### 3. Run the Project

Simply execute:

```sh
bash start.sh
```

This script will:
- Run the forecasting pipeline
- Start the FastAPI server for visualization

### 4. Access the FastAPI Endpoints

Once the server is running, open your browser and go to:

```
http://127.0.0.1:8000/docs
```

This will display the FastAPI interactive documentation.

## Running with Docker

You can also run the project in a Docker container:

```sh
docker-compose up --build
```


## Note:
The html files are being saved in the static direcotry of the project.