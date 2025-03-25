#!/bin/bash

echo "=== Testing ASR Service Directly ==="

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Ensure directories exist
mkdir -p "$PROJECT_ROOT/audio" "$PROJECT_ROOT/json"

# Ensure test audio file exists
if [ ! -f "$PROJECT_ROOT/audio/sample1.wav" ]; then
    echo "Warning: Test audio file not found. Generating one..."
    python "$PROJECT_ROOT/scripts/util/generate_sample1.py"
    cp "$PROJECT_ROOT/sample1.wav" "$PROJECT_ROOT/audio/"
fi

# Test with correct parameters
echo "Testing with 'file' field and 'language' parameter..."
curl -v -X POST \
  -F "file=@$PROJECT_ROOT/audio/sample1.wav" \
  -F "language=en" \
  http://localhost:8666/transcribe \
  -o "$PROJECT_ROOT/json/asr_response1.json"

# echo -e "\nTesting with different parameter formats..."
# curl -v -X POST \
#   -F "file=@$PROJECT_ROOT/audio/sample1.wav" \
#   -F "options.language=en" \
#   http://localhost:8666/transcribe \
#   -o "$PROJECT_ROOT/json/asr_response2.json"

echo -e "\nASR Response 1 (using 'file' field with 'language' parameter):"
cat "$PROJECT_ROOT/json/asr_response1.json" | jq 2>/dev/null || cat "$PROJECT_ROOT/json/asr_response1.json"

# echo -e "\nASR Response 2 (using 'file' field with options.language):"
# cat "$PROJECT_ROOT/json/asr_response2.json" | jq 2>/dev/null || cat "$PROJECT_ROOT/json/asr_response2.json"

# Check with file command to ensure we received proper JSON
echo -e "\nVerifying response file types:"
file "$PROJECT_ROOT/json/asr_response1.json"
# file "$PROJECT_ROOT/json/asr_response2.json" 