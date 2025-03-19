#!/bin/bash

# Define directory
TRANSLATION_DIR="/Users/bnr/work/github/lexi-shift"

# Navigate to directory
cd "$TRANSLATION_DIR"

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
pip install psutil structlog python-dotenv httpx

# Run the service
echo "Starting Translation service (Lexi-Shift) on port 8002..."
PORT=8002 python -m src.main

# Note: This script should be run in its own terminal window
# The service will stay in the foreground for easy debugging 