#!/bin/bash

echo "=== Testing NeuralBabel Pipeline ==="

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Ensure directories exist
mkdir -p "$PROJECT_ROOT/audio"

# Ensure test audio file exists
if [ ! -f "$PROJECT_ROOT/audio/test_audio.wav" ]; then
    echo "Warning: Test audio file not found. Generating one..."
    python "$PROJECT_ROOT/scripts/util/generate_test_audio.py"
    cp "$PROJECT_ROOT/test_audio.wav" "$PROJECT_ROOT/audio/"
fi

# Start NeuralBabel with custom environment variables
echo "Starting NeuralBabel..."
export ASR_SERVICE_ENDPOINT=http://localhost:8666
export TRANSLATION_SERVICE_ENDPOINT=http://localhost:8777
export TTS_SERVICE_ENDPOINT=http://localhost:8888
export PORT=8005
export LOG_LEVEL=INFO

# Run NeuralBabel in the background
cd "$PROJECT_ROOT"
source venv/bin/activate && python -m src.main &
NEURAL_BABEL_PID=$!

# Wait for NeuralBabel to start
echo "Waiting for NeuralBabel to start..."
sleep 5

# Check if NeuralBabel is running
echo "Checking health of NeuralBabel..."
HEALTH_RESPONSE=$(curl -s http://localhost:8005/health)
echo "Health response: $HEALTH_RESPONSE"

# Test the translation endpoint
echo "Testing the translation endpoint..."
curl -s -X POST \
  -F "audio=@$PROJECT_ROOT/audio/test_audio.wav" \
  -F "source_lang=en" \
  -F "target_lang=fr" \
  -F "audio_format=wav" \
  -F "voice=default" \
  http://localhost:8005/translate \
  -o "$PROJECT_ROOT/audio/response_audio.wav"

# Check if the response file was created
if [ -f "$PROJECT_ROOT/audio/response_audio.wav" ]; then
  FILESIZE=$(stat -f%z "$PROJECT_ROOT/audio/response_audio.wav" 2>/dev/null || stat -c%s "$PROJECT_ROOT/audio/response_audio.wav" 2>/dev/null)
  if [ -n "$FILESIZE" ] && [ "$FILESIZE" -gt 0 ]; then
    echo "Translation successful! Response saved to $PROJECT_ROOT/audio/response_audio.wav (size: $FILESIZE bytes)"
  else
    echo "Translation failed! Response file is empty."
  fi
else
  echo "Translation failed! No response file created."
fi

# Kill NeuralBabel
echo "Shutting down NeuralBabel..."
kill $NEURAL_BABEL_PID 2>/dev/null || true

echo "=== Test Complete ===" 