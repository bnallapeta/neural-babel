#!/bin/bash

# Set the service URL - replace with your actual ingress address
SERVICE_URL="http://neural-babel.default.74.224.102.71.nip.io"

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check if sample1.wav exists, if not try to use test_audio.wav
if [ ! -f "$PROJECT_ROOT/audio/sample1.wav" ]; then
    if [ -f "$PROJECT_ROOT/audio/test_audio.wav" ]; then
        echo "Using test_audio.wav as sample1.wav..."
        cp "$PROJECT_ROOT/audio/test_audio.wav" "$PROJECT_ROOT/audio/sample1.wav"
    elif [ -f "$PROJECT_ROOT/test_audio.wav" ]; then
        echo "Using test_audio.wav from project root..."
        cp "$PROJECT_ROOT/test_audio.wav" "$PROJECT_ROOT/audio/sample1.wav"
    else
        echo "No test audio file found. Please create one first."
        exit 1
    fi
fi

# Check if the service is healthy
echo "Checking service health..."
HEALTH_RESPONSE=$(curl -s $SERVICE_URL/health)
echo "Health check response: $HEALTH_RESPONSE"

# Get supported languages
echo -e "\nGetting supported languages..."
curl -s $SERVICE_URL/languages | jq . 2>/dev/null || echo "Failed to get languages or jq not installed"

# Translate an audio file
echo -e "\nTranslating audio file..."
curl -X POST \
  -F "audio=@$PROJECT_ROOT/audio/sample1.wav" \
  -F "source_lang=en" \
  -F "target_lang=fr" \
  -F "audio_format=wav" \
  -F "voice=default" \
  $SERVICE_URL/translate \
  -o $PROJECT_ROOT/audio/deployed_translation.wav

echo -e "\nTranslation complete. Output saved to $PROJECT_ROOT/audio/deployed_translation.wav"

# Play the translated audio if possible
if command -v afplay &> /dev/null; then
  echo -e "\nPlaying translated audio..."
  afplay $PROJECT_ROOT/deployed_translation.wav
elif command -v aplay &> /dev/null; then
  echo -e "\nPlaying translated audio..."
  aplay $PROJECT_ROOT/deployed_translation.wav
else
  echo -e "\nNo audio player found. Please listen to deployed_translation.wav manually."
fi

echo -e "\nTest complete!"

# If anything went wrong, check the pod logs
echo -e "\nTo view service logs, use the following commands:"
echo "export KUBECONFIG=\"$KUBECONFIG\""
echo "POD_NAME=\$(kubectl get pods -l app=neural-babel -o jsonpath=\"{.items[0].metadata.name}\")"
echo "kubectl logs \$POD_NAME" 