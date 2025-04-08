#!/bin/bash

# Set service URL
SERVICE_URL="http://neural-babel.default.74.224.102.71.nip.io"

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
GRAY='\033[0;90m'
YELLOW='\033[0;33m'
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

# Function to print timestamp
timestamp() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')]${NC} $1"
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

print_text "Starting serial request test (30 requests with 2-second intervals)"
timestamp "Test started"

# Configuration
TOTAL_REQUESTS=30
REQUEST_DELAY=2  # seconds between requests

# Send requests serially (without waiting for completion)
success_count=0
for ((i=1; i<=TOTAL_REQUESTS; i++)); do
    timestamp "Sending request $i of $TOTAL_REQUESTS..."
    
    # Send the request in the background
    curl -s -X POST "$SERVICE_URL/translate" \
        -F "audio=@$INPUT_AUDIO" \
        -F "source_lang=$SOURCE_LANG" \
        -F "target_lang=$TARGET_LANG" \
        -F "audio_format=wav" \
        -F "voice=default" \
        --output "scripts/audio/concurrent_test/translation_$i.wav" &
    
    print_success "Request $i sent"
    
    # Wait before next request (if not the last one)
    if [ $i -lt $TOTAL_REQUESTS ]; then
        timestamp "Waiting $REQUEST_DELAY seconds before next request..."
        sleep $REQUEST_DELAY
    fi
done

timestamp "All requests sent, waiting for completion..."
wait
timestamp "All requests completed processing"

# Check results
print_text "Results"
success_count=0
for i in $(seq 1 $TOTAL_REQUESTS); do
    if [ -f "scripts/audio/concurrent_test/translation_$i.wav" ] && [ -s "scripts/audio/concurrent_test/translation_$i.wav" ]; then
        print_success "Request $i completed successfully"
        ((success_count++))
    else
        print_error "Request $i failed"
    fi
done

print_text "Summary"
timestamp "Test finished"
echo "Total requests: $TOTAL_REQUESTS"
echo "Successful requests: $success_count"
echo "Delay between requests: $REQUEST_DELAY seconds"

if [ $success_count -eq $TOTAL_REQUESTS ]; then
    print_success "All requests completed successfully"
else
    print_error "Some requests failed ($((TOTAL_REQUESTS-success_count)) failures)"
    print_error "KServe scaling might need investigation."
fi 