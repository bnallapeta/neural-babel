#!/bin/bash

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Ensure directories exist
mkdir -p "$PROJECT_ROOT/audio"

# Ensure test audio file exists and copy it as input.wav if needed
if [ ! -f "$PROJECT_ROOT/audio/sample1.wav" ]; then
    echo "Input audio file not found. Checking for test_audio.wav..."
    
    if [ -f "$PROJECT_ROOT/test_audio.wav" ]; then
        echo "Found test_audio.wav. Copying to input.wav..."
        cp "$PROJECT_ROOT/test_audio.wav" "$PROJECT_ROOT/audio/input.wav"
    elif [ -f "$PROJECT_ROOT/audio/test_audio.wav" ]; then
        echo "Found test_audio.wav in audio directory. Copying to input.wav..."
        cp "$PROJECT_ROOT/audio/test_audio.wav" "$PROJECT_ROOT/audio/input.wav"
    else
        echo "No test audio found. Generating one..."
        python "$PROJECT_ROOT/scripts/util/generate_test_audio.py"
        cp "$PROJECT_ROOT/test_audio.wav" "$PROJECT_ROOT/audio/input.wav"
    fi
fi

# Activate virtual environment
source "$PROJECT_ROOT/venv/bin/activate"

# Run the test script
python "$SCRIPT_DIR/run_detailed_test.py"

# Play the audio files if possible
if command -v afplay &> /dev/null; then
  echo -e "\nPlaying original audio (sample1.wav)..."
  afplay "$PROJECT_ROOT/audio/sample1.wav"
  echo -e "\nPlaying translated audio (translated.wav)..."
  afplay "$PROJECT_ROOT/audio/translated.wav"
elif command -v aplay &> /dev/null; then
  echo -e "\nPlaying original audio (input.wav)..."
  aplay "$PROJECT_ROOT/audio/input.wav"
  echo -e "\nPlaying translated audio (translated.wav)..."
  aplay "$PROJECT_ROOT/audio/translated.wav"
else
  echo -e "\nAudio player not found. Please listen to the audio files manually:"
  echo "- Original: $PROJECT_ROOT/audio/input.wav"
  echo "- Translated: $PROJECT_ROOT/audio/translated.wav"
fi

echo -e "\n=== Test Complete ===" 