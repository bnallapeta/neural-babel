#!/bin/bash

# Set service URL - hardcoded to ensure it works
SERVICE_URL="http://neural-babel.default.74.224.102.71.nip.io"

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
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
mkdir -p scripts/audio/batch_test

# Warm-up phase - Send 5 sequential requests to "wake up" kube-whisperer
# These requests are not logged as they might fail, just to get the service ready
WARMUP_REQUESTS=5
WARMUP_DELAY=1  # seconds between warm-up requests

# Hide the warm-up process from user output
echo -e "\n${GRAY}Warming up services (this may take a moment)...${NC}"
for ((i=1; i<=WARMUP_REQUESTS; i++)); do
    # Send warm-up request silently and sequentially (no & at the end)
    curl -s -X POST "$SERVICE_URL/translate" \
        -F "audio=@$INPUT_AUDIO" \
        -F "source_lang=$SOURCE_LANG" \
        -F "target_lang=$TARGET_LANG" \
        -F "audio_format=wav" \
        -F "voice=default" \
        --output "/dev/null" > /dev/null 2>&1
    
    # Show subtle progress indicator
    echo -n -e "${GRAY}.${NC}"
    
    # Wait before next warm-up request
    sleep $WARMUP_DELAY
done
echo -e "\n${GRAY}Warm-up completed${NC}"

# Wait just a brief moment to allow services to start scaling up
sleep 2

print_text "Starting batch concurrent test (30 requests in batches of 6 with 2-second intervals)"
timestamp "Test started"

# Configuration
TOTAL_REQUESTS=30
BATCH_SIZE=6
BATCH_DELAY=2  # seconds between batches

# Calculate total number of batches (with proper integer arithmetic)
TOTAL_BATCHES=$((TOTAL_REQUESTS / BATCH_SIZE))

# Send requests in batches
for ((batch=0; batch<TOTAL_BATCHES; batch++)); do
    batch_start=$((batch * BATCH_SIZE + 1))
    batch_end=$((batch_start + BATCH_SIZE - 1))
    
    timestamp "Sending batch $((batch+1)) (requests $batch_start-$batch_end)..."
    
    # Send batch of requests simultaneously
    for ((i=batch_start; i<=batch_end; i++)); do
        # Send the request in the background
        curl -s -X POST "$SERVICE_URL/translate" \
            -F "audio=@$INPUT_AUDIO" \
            -F "source_lang=$SOURCE_LANG" \
            -F "target_lang=$TARGET_LANG" \
            -F "audio_format=wav" \
            -F "voice=default" \
            --output "scripts/audio/batch_test/translation_$i.wav" &
        
        print_success "Request $i sent"
    done
    
    # Wait before next batch (if not the last batch)
    if [ $batch -lt $((TOTAL_BATCHES-1)) ]; then
        timestamp "Batch $((batch+1)) sent. Waiting $BATCH_DELAY seconds before next batch..."
        sleep $BATCH_DELAY
    else
        timestamp "Final batch sent."
    fi
done

timestamp "All requests sent, waiting for completion..."
wait
timestamp "All requests completed processing"

# Check results
print_text "Results"
success_count=0
for i in $(seq 1 $TOTAL_REQUESTS); do
    if [ -f "scripts/audio/batch_test/translation_$i.wav" ] && [ -s "scripts/audio/batch_test/translation_$i.wav" ]; then
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
echo "Batch size: $BATCH_SIZE"
echo "Delay between batches: $BATCH_DELAY seconds"

if [ $success_count -eq $TOTAL_REQUESTS ]; then
    print_success "All requests completed successfully"
else
    print_error "Some requests failed ($((TOTAL_REQUESTS-success_count)) failures)"
    print_error "KServe scaling might need investigation."
fi 