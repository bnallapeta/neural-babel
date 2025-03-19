#!/bin/bash

echo "=== Testing Translation Service Directly ==="

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Ensure directories exist
mkdir -p "$PROJECT_ROOT/json"

# Test translation
echo "Testing text translation..."
curl -v -X POST \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test message for translation.", "options": {"source_lang": "en", "target_lang": "fr"}}' \
  http://localhost:8777/translate \
  -o "$PROJECT_ROOT/json/translation_response.json"

# Check response
echo -e "\nTranslation response:"
cat "$PROJECT_ROOT/json/translation_response.json" | jq 2>/dev/null || cat "$PROJECT_ROOT/json/translation_response.json" 