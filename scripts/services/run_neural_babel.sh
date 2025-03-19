#!/bin/bash

# Define directory
NEURAL_BABEL_DIR="/Users/bnr/work/github/neural-babel"

# Navigate to directory
cd "$NEURAL_BABEL_DIR"

# Activate virtual environment
source venv/bin/activate

# Run the service
echo "Starting NeuralBabel on port 8005..."
PORT=8005 python -m src.main

# Note: This script should be run in its own terminal window
# The service will stay in the foreground for easy debugging 