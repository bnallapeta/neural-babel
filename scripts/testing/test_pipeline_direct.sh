#!/bin/bash

echo "=== Testing NeuralBabel Pipeline with Direct Service URLs ==="

# Make sure nothing is running on port 8005
echo "Checking for existing processes on port 8005..."
EXISTING_PID=$(lsof -ti:8005)
if [ ! -z "$EXISTING_PID" ]; then
  echo "Killing existing process on port 8005: $EXISTING_PID"
  kill $EXISTING_PID
  sleep 2
fi

# Start NeuralBabel with custom environment variables
echo "Starting NeuralBabel with direct service URLs..."
export ASR_SERVICE_ENDPOINT=http://localhost:8666
export TRANSLATION_SERVICE_ENDPOINT=http://localhost:8777
export TTS_SERVICE_ENDPOINT=http://localhost:8888
export PORT=8005
export LOG_LEVEL=DEBUG

# Activate virtual environment and run NeuralBabel
source venv/bin/activate
python -m src.main > neural_babel.log 2>&1 &
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
curl -v -X POST \
  -F "audio=@test_audio.wav" \
  -F "source_lang=en" \
  -F "target_lang=fr" \
  -F "audio_format=wav" \
  -F "voice=default" \
  http://localhost:8005/translate \
  -o response_audio.wav

# Check if the response file was created
if [ -f "response_audio.wav" ]; then
  FILESIZE=$(stat -f%z "response_audio.wav")
  if [ "$FILESIZE" -gt 1000 ]; then
    echo "Translation successful! Response saved to response_audio.wav (size: $FILESIZE bytes)"
  else
    echo "Response file created but seems too small (size: $FILESIZE bytes). It might contain an error message:"
    cat response_audio.wav | jq 2>/dev/null || cat response_audio.wav
  fi
else
  echo "Translation failed! No response file created."
fi

# Show the NeuralBabel logs
echo -e "\nNeuralBabel logs (last 20 lines):"
tail -20 neural_babel.log

# Kill NeuralBabel
echo "Shutting down NeuralBabel..."
kill $NEURAL_BABEL_PID
sleep 1

echo "=== Test Complete ===" 