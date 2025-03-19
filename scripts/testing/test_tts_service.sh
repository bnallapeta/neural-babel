#!/bin/bash

echo "=== Testing TTS Service Directly ==="

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Ensure directories exist
mkdir -p "$PROJECT_ROOT/audio" "$PROJECT_ROOT/json"

# Test text synthesis
echo "Testing text synthesis..."
curl -v -X POST \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test message for speech synthesis.", "language": "en", "voice": "default", "audio_format": "wav"}' \
  http://localhost:8888/synthesize \
  -o "$PROJECT_ROOT/audio/tts_response.wav"

# Check response
echo -e "\nResponse file size:"
ls -l "$PROJECT_ROOT/audio/tts_response.wav" 2>/dev/null || echo "No response file was created."

echo -e "\nFile type:"
file "$PROJECT_ROOT/audio/tts_response.wav" 2>/dev/null || echo "File not found." 