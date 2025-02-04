#!/bin/bash

# Change to the script's directory
cd "$(dirname "$0")" || exit

# Path to your virtual environment (relative to the script's location)
VENV_PATH=".venv"

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Path to your Python script (relative to the script's location)
PYTHON_SCRIPT="src/PortfolioOptimizer/pipeline/pipeline.py"

# Run the Python script
python3 "$PYTHON_SCRIPT"
