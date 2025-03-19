#!/bin/bash

# Exit on error
set -e

# Define variables for service directories
WHISPER_DIR="/Users/bnr/work/github/whisper"
TRANSLATION_DIR="/Users/bnr/work/github/lexi-shift"
VOX_RAGA_DIR="/Users/bnr/work/github/vox-raga"
NEURAL_BABEL_DIR="/Users/bnr/work/github/neural-babel"

# Kill any existing services
echo "Stopping any existing services..."
pkill -f "python.*src.main" || true
pkill -f "python.*src.serve" || true

echo "===== Starting real services ====="

# Common additional dependencies for all services
COMMON_DEPS="psutil structlog python-dotenv pyyaml pytest pytest-cov pytest-asyncio httpx"

# Start Whisper service (ASR)
echo "Starting ASR service (Whisper) on port 8001..."
cd "$WHISPER_DIR"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment for ASR service..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    # Install additional dependencies that might be missing
    pip install $COMMON_DEPS
    pip install -e .
    deactivate
else
    # Ensure common dependencies are installed
    source venv/bin/activate
    pip install $COMMON_DEPS
    deactivate
fi

echo "Running ASR service..."
WHISPER_PYTHON="$WHISPER_DIR/venv/bin/python"
cd "$WHISPER_DIR"
PORT=8001 $WHISPER_PYTHON src/serve.py &
ASR_PID=$!
echo "ASR service started with PID: $ASR_PID"
sleep 2  # Brief pause to let process start
cd - > /dev/null

# Start Translation service
echo "Starting Translation service (Lexi-Shift) on port 8002..."
cd "$TRANSLATION_DIR"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment for Translation service..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    # Install additional dependencies that might be missing
    pip install $COMMON_DEPS
    deactivate
else
    # Ensure common dependencies are installed
    source venv/bin/activate
    pip install $COMMON_DEPS
    deactivate
fi

echo "Running Translation service..."
TRANSLATION_PYTHON="$TRANSLATION_DIR/venv/bin/python"
cd "$TRANSLATION_DIR"
PORT=8002 $TRANSLATION_PYTHON -m src.main &
TRANSLATION_PID=$!
echo "Translation service started with PID: $TRANSLATION_PID"
sleep 2  # Brief pause to let process start
cd - > /dev/null

# Start TTS service
echo "Starting TTS service (Vox-Raga) on port 8003..."
cd "$VOX_RAGA_DIR"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment for TTS service..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    # Install additional dependencies that might be missing
    pip install $COMMON_DEPS
    deactivate
else
    # Ensure common dependencies are installed
    source venv/bin/activate
    pip install $COMMON_DEPS
    deactivate
fi

echo "Running TTS service..."
TTS_PYTHON="$VOX_RAGA_DIR/venv/bin/python"
cd "$VOX_RAGA_DIR"
PORT=8003 $TTS_PYTHON -m src.main &
TTS_PID=$!
echo "TTS service started with PID: $TTS_PID"
sleep 2  # Brief pause to let process start
cd - > /dev/null

# Wait for services to start
echo "Waiting for services to start..."
sleep 10  # Increased wait time to give services more time to initialize

# Check if services are running
echo "Checking if services are running..."
ps -p $ASR_PID > /dev/null || echo "WARNING: ASR service not running!"
ps -p $TRANSLATION_PID > /dev/null || echo "WARNING: Translation service not running!"
ps -p $TTS_PID > /dev/null || echo "WARNING: TTS service not running!"

# Start the NeuralBabel application
echo "Starting NeuralBabel on port 8005..."
cd "$NEURAL_BABEL_DIR"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment for NeuralBabel..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
fi

NEURAL_BABEL_PYTHON="$NEURAL_BABEL_DIR/venv/bin/python"
PORT=8005 $NEURAL_BABEL_PYTHON -m src.main &
MAIN_PID=$!
echo "NeuralBabel started with PID: $MAIN_PID"

# Function to clean up processes
cleanup() {
    echo "Cleaning up processes..."
    kill $ASR_PID $TRANSLATION_PID $TTS_PID $MAIN_PID 2>/dev/null || true
    echo "All processes terminated."
    exit 0
}

# Register cleanup function
trap cleanup INT TERM

echo ""
echo "=============================================================="
echo "All real services are running!"
echo "=============================================================="
echo ""
echo "NeuralBabel API is available at: http://localhost:8005"
echo "API Documentation: http://localhost:8005/docs"
echo ""
echo "Services:"
echo "- ASR (Whisper): http://localhost:8001"
echo "- Translation (Lexi-Shift): http://localhost:8002"
echo "- TTS (Vox-Raga): http://localhost:8003"
echo ""
echo "Test commands:"
echo "  curl -s http://localhost:8005/languages"
echo "  curl -s http://localhost:8005/health"
echo "  curl -s http://localhost:8005/ready"
echo "  curl -s http://localhost:8005/live"
echo ""
echo "To test translation:"
echo "  python generate_test_audio.py"
echo "  curl -s -X POST -F \"audio=@test_audio.wav\" -F \"source_lang=en\" -F \"target_lang=fr\" -F \"audio_format=wav\" -F \"voice=default\" http://localhost:8005/translate -o response_audio.wav"
echo ""
echo "Press Ctrl+C to stop all services."
echo "=============================================================="

# Keep the script running
wait 