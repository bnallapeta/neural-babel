#!/bin/bash

echo "=== NeuralBabel Test Runner ==="
echo "This script provides easy access to run different tests."

# Get absolute path of the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

function print_help {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --services, -s    Test all services for health"
    echo "  --pipeline, -p    Test the complete pipeline"
    echo "  --direct, -d      Test the pipeline directly without starting NeuralBabel"
    echo "  --asr, -a         Test only ASR service"
    echo "  --tts, -t         Test only TTS service"
    echo "  --translate, -l   Test only Translation service"
    echo "  --manual, -m      Run manual test with detailed output"
    echo "  --help, -h        Print this help message"
    echo ""
    echo "Example: $0 --pipeline"
}

# No arguments provided, show help
if [ $# -eq 0 ]; then
    print_help
    exit 1
fi

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --services|-s)
            echo "Testing all services for health..."
            python "${SCRIPT_DIR}/scripts/testing/test_services.py"
            exit 0
            ;;
        --pipeline|-p)
            echo "Testing the complete pipeline..."
            bash "${SCRIPT_DIR}/scripts/testing/test_pipeline.sh"
            exit 0
            ;;
        --direct|-d)
            echo "Testing the pipeline directly..."
            bash "${SCRIPT_DIR}/scripts/testing/test_pipeline_direct.sh"
            exit 0
            ;;
        --asr|-a)
            echo "Testing ASR service..."
            bash "${SCRIPT_DIR}/scripts/testing/test_asr_service.sh"
            exit 0
            ;;
        --tts|-t)
            echo "Testing TTS service..."
            bash "${SCRIPT_DIR}/scripts/testing/test_tts_service.sh"
            exit 0
            ;;
        --translate|-l)
            echo "Testing Translation service..."
            bash "${SCRIPT_DIR}/scripts/testing/test_translation_service.sh"
            exit 0
            ;;
        --manual|-m)
            echo "Running manual test with detailed output..."
            bash "${SCRIPT_DIR}/scripts/testing/manual/run_test.sh"
            exit 0
            ;;
        --help|-h)
            print_help
            exit 0
            ;;
        *)
            echo "Error: Unknown option $1"
            print_help
            exit 1
            ;;
    esac
done 