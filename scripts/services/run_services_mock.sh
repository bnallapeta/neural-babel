#!/bin/bash

# Exit on error
set -e

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Kill any existing services
echo "Stopping any existing services..."
pkill -f "python.*run_mock" || true
pkill -f "python.*src.main" || true

# Activate virtual environment
source "$PROJECT_ROOT/venv/bin/activate"

# Start mock services in background
echo "Starting ASR service on port 8001..."
python "$SCRIPT_DIR/run_mock_asr.py" --port 8001 &
ASR_PID=$!

echo "Starting Translation service on port 8002..."
python "$SCRIPT_DIR/run_mock_translation.py" --port 8002 &
TRANSLATION_PID=$!

echo "Starting TTS service on port 8003..."
python "$SCRIPT_DIR/run_mock_tts.py" --port 8003 &
TTS_PID=$!

# Wait for services to start
echo "Waiting for services to start..."
sleep 3

# Start the main application
echo "Starting NeuralBabel on port 8005..."
cd "$PROJECT_ROOT"
PORT=8005 python -m src.main &
MAIN_PID=$!

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
echo "All services are running!"
echo "=============================================================="
echo ""
echo "NeuralBabel API is available at: http://localhost:8005"
echo "API Documentation: http://localhost:8005/docs"
echo ""
echo "Services:"
echo "- ASR: http://localhost:8001"
echo "- Translation: http://localhost:8002"
echo "- TTS: http://localhost:8003"
echo ""
echo "Test commands:"
echo "  curl -s http://localhost:8005/languages"
echo "  curl -s http://localhost:8005/health"
echo "  curl -s http://localhost:8005/ready"
echo "  curl -s http://localhost:8005/live"
echo ""
echo "To test translation:"
echo "  python $PROJECT_ROOT/scripts/util/generate_test_audio.py"
echo "  curl -s -X POST -F \"audio=@$PROJECT_ROOT/audio/test_audio.wav\" -F \"source_lang=en\" -F \"target_lang=fr\" -F \"audio_format=wav\" -F \"voice=default\" http://localhost:8005/translate -o $PROJECT_ROOT/audio/response_audio.wav"
echo ""
echo "Press Ctrl+C to stop all services."
echo "=============================================================="

# Keep the script running
wait 