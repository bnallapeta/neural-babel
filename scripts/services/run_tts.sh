#!/bin/bash

# Define directory
VOX_RAGA_DIR="/Users/bnr/work/github/vox-raga"

# Navigate to directory
cd "$VOX_RAGA_DIR"

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
pip install psutil structlog python-dotenv httpx

# Run the service
echo "Starting TTS service (Vox-Raga) on port 8003..."
PORT=8003 python -m src.main

# Note: This script should be run in its own terminal window
# The service will stay in the foreground for easy debugging 