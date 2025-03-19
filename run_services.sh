#!/bin/bash

echo "=== NeuralBabel Service Runner ==="
echo "This script provides easy access to start all required services."

# Get absolute path of the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

function print_help {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --mock, -m       Run mock services (for development and testing)"
    echo "  --real, -r       Run real services (all in a separate terminals)"
    echo "  --asr, -a        Run only ASR service"
    echo "  --tts, -t        Run only TTS service"
    echo "  --translate, -s  Run only Translation service"
    echo "  --neural, -n     Run only NeuralBabel service"
    echo "  --help, -h       Print this help message"
    echo ""
    echo "Example: $0 --real"
}

# No arguments provided, show help
if [ $# -eq 0 ]; then
    print_help
    exit 1
fi

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --mock|-m)
            echo "Running mock services..."
            bash "${SCRIPT_DIR}/scripts/services/run_services_mock.sh"
            exit 0
            ;;
        --real|-r)
            echo "Running real services (check separate terminal windows)..."
            bash "${SCRIPT_DIR}/scripts/services/run_services_real.sh"
            exit 0
            ;;
        --asr|-a)
            echo "Running ASR service..."
            bash "${SCRIPT_DIR}/scripts/services/run_asr.sh"
            exit 0
            ;;
        --tts|-t)
            echo "Running TTS service..."
            bash "${SCRIPT_DIR}/scripts/services/run_tts.sh"
            exit 0
            ;;
        --translate|-s)
            echo "Running Translation service..."
            bash "${SCRIPT_DIR}/scripts/services/run_translation.sh"
            exit 0
            ;;
        --neural|-n)
            echo "Running NeuralBabel service..."
            bash "${SCRIPT_DIR}/scripts/services/run_neural_babel.sh"
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