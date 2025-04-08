#!/bin/bash

# Set service URL
SERVICE_URL="http://neural-babel.default.74.224.102.71.nip.io"

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

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

# Make the script executable
chmod +x "$0"

# Check service health
print_text "Checking service health"
if curl -s "$SERVICE_URL/health" | grep -q "status\":\"ok"; then
    print_success "Service is healthy"
else
    print_error "Service is not healthy"
    exit 1
fi

# Check if input audio file exists
INPUT_AUDIO="scripts/audio/sample1.wav"
if [ ! -f "$INPUT_AUDIO" ]; then
    print_error "Input audio file not found: $INPUT_AUDIO"
    exit 1
fi

# Set source and target languages
SOURCE_LANG="en"
TARGET_LANG="fr"

# Create directory for output files
mkdir -p scripts/audio/concurrent_test

print_text "Starting concurrent request test (15 requests with 3-second intervals)"

# Send 15 requests with 3-second gaps
for i in {1..15}; do
    echo -e "\nSending request $i of 15..."
    
    # Send the request in the background
    curl -s -X POST "$SERVICE_URL/translate" \
        -F "audio=@$INPUT_AUDIO" \
        -F "source_lang=$SOURCE_LANG" \
        -F "target_lang=$TARGET_LANG" \
        -F "audio_format=wav" \
        -F "voice=default" \
        --output "scripts/audio/concurrent_test/translation_$i.wav" &
    
    print_success "Request $i sent"
    
    # Wait 3 seconds before next request
    if [ $i -lt 15 ]; then
        echo "Waiting 3 seconds before next request..."
        sleep 3
    fi
done

print_text "Waiting for all requests to complete..."
wait

# Check results
print_text "Results"
success_count=0
for i in {1..15}; do
    if [ -f "scripts/audio/concurrent_test/translation_$i.wav" ] && [ -s "scripts/audio/concurrent_test/translation_$i.wav" ]; then
        print_success "Request $i completed successfully"
        ((success_count++))
    else
        print_error "Request $i failed"
    fi
done

print_text "Summary"
echo "Total requests: 15"
echo "Successful requests: $success_count"

if [ $success_count -eq 15 ]; then
    print_success "All requests completed successfully"
else
    print_error "Some requests failed. KServe scaling might need investigation."
fi 