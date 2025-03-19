# NeuralBabel

NeuralBabel is a comprehensive speech-to-speech translation system that integrates automatic speech recognition (ASR), machine translation, and text-to-speech (TTS) services to provide seamless translation between different languages.

## Features

- **Speech-to-Speech Translation**: Translate spoken content from one language to another
- **Modular Architecture**: Each component (ASR, Translation, TTS) is a separate service
- **Multiple Language Support**: Support for multiple language pairs
- **API-First Design**: RESTful API for easy integration with other applications
- **Kubernetes Ready**: Deployment configurations for Kubernetes
- **Comprehensive Testing**: Extensive test suite for all components

## Project Structure

```
neural-babel/
├── audio/                  # Audio files used for testing
├── docs/                   # Documentation files
├── json/                   # JSON files (API responses, etc.)
├── k8s/                    # Kubernetes deployment configurations
├── logs/                   # Log files
├── scripts/                # Scripts for various operations
│   ├── services/           # Scripts for running individual services
│   ├── testing/            # Scripts for testing
│   │   └── manual/         # Manual testing scripts
│   └── util/               # Utility scripts
├── src/                    # Source code
│   ├── api/                # API endpoints and models
│   ├── clients/            # Service clients
│   ├── config/             # Configuration
│   ├── orchestrator/       # Pipeline orchestration
│   └── utils/              # Utilities
├── tests/                  # Automated tests
├── .env                    # Environment variables
├── Dockerfile              # Docker build configuration
├── LICENSE                 # License information
├── Makefile                # Make targets
├── README.md               # This file
├── requirements.txt        # Python dependencies
├── run_services.sh         # Main script to run services
└── run_tests.sh            # Main script to run tests
```

## Quick Start

### Running Services

NeuralBabel provides a convenient script to run all required services:

```bash
# Show help
./run_services.sh

# Run all services with mock implementations (for development)
./run_services.sh --mock

# Run all real services (in separate terminals)
./run_services.sh --real

# Run specific services
./run_services.sh --asr      # Run ASR service
./run_services.sh --tts      # Run TTS service
./run_services.sh --translate # Run Translation service
./run_services.sh --neural   # Run NeuralBabel service
```

### Running Tests

NeuralBabel includes a comprehensive test suite:

```bash
# Show help
./run_tests.sh

# Test all services for health
./run_tests.sh --services

# Test the complete pipeline
./run_tests.sh --pipeline

# Test specific services
./run_tests.sh --asr       # Test ASR service
./run_tests.sh --tts       # Test TTS service
./run_tests.sh --translate # Test Translation service

# Run manual test with detailed output
./run_tests.sh --manual
```

## API Usage

### Translation Endpoint

```bash
curl -X POST \
  -F "audio=@audio/sample1.wav" \
  -F "source_lang=en" \
  -F "target_lang=fr" \
  -F "audio_format=wav" \
  -F "voice=default" \
  http://localhost:8005/translate \
  -o response_audio.wav
```

### Other Endpoints

- Health check: `curl -s http://localhost:8005/health`
- Languages: `curl -s http://localhost:8005/languages`
- Configuration: `curl -s http://localhost:8005/config`

## Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables: Copy `.env.example` to `.env` and adjust as needed
4. Run services in development mode: `./run_services.sh --mock`
5. Run tests to verify setup: `./run_tests.sh --services`

## Deployment

NeuralBabel can be deployed to Kubernetes using the provided configurations:

```bash
# Build the Docker image
docker build -t neural-babel:latest .

# Deploy to Kubernetes
kubectl apply -f k8s/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.