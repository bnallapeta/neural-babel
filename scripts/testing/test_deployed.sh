#!/bin/bash

# Set service URL
SERVICE_URL="http://neural-babel.default.74.224.102.71.nip.io"

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Spinner animation
spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf "\r[%c] %s" "$spinstr" "$2"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
    done
    printf "\r   \r"
}

# Function to print formatted text
print_text() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Function to print success message
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error message
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Initialize Neural Babel Translation Pipeline
print_text "Initializing Neural Babel Translation Pipeline"

# Check service health
echo "Checking service health..."
if curl -s "$SERVICE_URL/health" | grep -q "status\":\"ok"; then
    print_success "Service is healthy"
else
    print_error "Service is not healthy"
    exit 1
fi

# # Get available language pairs
# echo -e "\nAvailable language pairs:"
# curl -s "$SERVICE_URL/languages" | jq -r '.language_pairs[] | "• \(.source_name) → \(.target_name)"'

# Start translation process
print_text "Starting Translation Process"

# Check if input audio file exists
INPUT_AUDIO="scripts/audio/sample1.wav"
if [ ! -f "$INPUT_AUDIO" ]; then
    print_error "Input audio file not found: $INPUT_AUDIO"
    exit 1
fi

# Set source and target languages
SOURCE_LANG="en"
TARGET_LANG="fr"

# Run the complete translation pipeline
echo -e "\nRunning translation pipeline..."
(curl -s -X POST "$SERVICE_URL/translate" \
    -F "audio=@$INPUT_AUDIO" \
    -F "source_lang=$SOURCE_LANG" \
    -F "target_lang=$TARGET_LANG" \
    -F "audio_format=wav" \
    -F "voice=default" \
    --output "scripts/audio/deployed_translation.wav") &
spinner $! "Processing translation"

# Check if the output file was created and has content
if [ -f "scripts/audio/deployed_translation.wav" ] && [ -s "scripts/audio/deployed_translation.wav" ]; then
    print_success "Translation completed successfully"
    echo -e "\nOutput audio file saved to: scripts/audio/deployed_translation.wav"
    
    # Play the translated audio
    echo -e "\nPlaying translated audio..."
    afplay "scripts/audio/deployed_translation.wav"
else
    print_error "Translation failed. Please check the service logs."
    exit 1
fi

# Print summary
print_text "Translation Summary"
echo "Source Language: English"
echo "Target Language: French"
print_success "Translation completed successfully"