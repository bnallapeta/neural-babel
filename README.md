# NeuralBabel

NeuralBabel is a comprehensive speech-to-speech translation system that integrates automatic speech recognition (ASR | Whisper), language translation (NLLB), and text-to-speech (TTS | Coqui) services to provide seamless translation between different languages.

## Features

- **Speech-to-Speech Translation**: Translate spoken content from one language to another
- **Modular Architecture**: Each component (ASR, Translation, TTS) is a separate service
- **Multiple Language Support**: Support for multiple language pairs
- **API-First Design**: RESTful API for easy integration with other applications
- **Kubernetes Ready**: Deployment configurations for Kubernetes

## Project Structure

```
neural-babel/
├── audio/                  # Audio files used for testing
├── k8s/                    # Kubernetes deployment configurations
├── scripts/                # Scripts for various operations
│   └── testing/            # Scripts for testing
├── src/                    # Source code
│   ├── api/                # API endpoints and models
│   ├── clients/            # Service clients
│   ├── orchestrator/       # Pipeline orchestration
│   └── utils/              # Utilities
├── .env                    # Environment variables
├── Dockerfile              # Docker build configuration
└── requirements.txt        # Python dependencies
```

## How to Run

### Prerequisites

1. Python 3.9+
2. Virtual environment (recommended)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/neural-babel.git
   cd neural-babel
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Services

NeuralBabel requires three component services:

1. ASR Service (Kube-Whisperer)
2. Translation Service (Lexi-Shift)
3. TTS Service (Vox-Raga)

These services are running at the following endpoints:
- ASR: http://kube-whisperer.default.<external-ip>.nip.io
- Translation: http://translation-service.default.<external-ip>.nip.io
- TTS: http://vox-raga.default.<external-ip>.nip.io

*Note that nip.io is a free service that provides a way to access services running on a local machine from the internet. The external-ip is the IP address of the machine running the services. For a production environment, you would need to deploy the services to a cloud provider and use the public IP address of the services.*

To run the NeuralBabel orchestrator:

```bash
python -m src.main
```

### Testing the Pipeline

To test the complete speech-to-speech translation pipeline:

```bash
# Run the test script
./scripts/testing/run_test.sh
```

This script will:
1. Ensure the required audio files exist
2. Test the ASR service to convert speech to text
3. Test the translation service to translate the text
4. Test the TTS service to convert the translated text back to speech
5. Play the original and translated audio files (if compatible audio player is available)

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
  -o translated_audio.wav
```

### Other Endpoints

- Health check: `curl -s http://localhost:8005/health`
- Languages: `curl -s http://localhost:8005/languages`
- Configuration: `curl -s http://localhost:8005/config`

## Deployment

NeuralBabel can be deployed to Kubernetes using the provided configurations:

```bash
# Build the Docker image
docker build -t neural-babel:latest .

# Deploy to Kubernetes
kubectl apply -f k8s/
```