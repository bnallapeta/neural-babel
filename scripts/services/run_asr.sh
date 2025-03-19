#!/bin/bash

# Define directory
WHISPER_DIR="/Users/bnr/work/github/whisper"

# Navigate to directory
cd "$WHISPER_DIR"

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
# pip install psutil structlog python-dotenv httpx

# Run the service
echo "Starting ASR service (Whisper) on port 8001..."
PORT=8001 python -m src.serve

# Note: This script should be run in its own terminal window
# The service will stay in the foreground for easy debugging 