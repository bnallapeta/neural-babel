# NeuralBabel

NeuralBabel is a comprehensive speech-to-speech translation system that integrates automatic speech recognition (ASR | Whisper), language translation (NLLB), and text-to-speech (TTS | Coqui) services to provide seamless translation between different languages.

## Features

- **Speech-to-Speech Translation**: Translate spoken content from one language to another
- **Modular Architecture**: Each component (ASR, Translation, TTS) is a separate service
- **Multiple Language Support**: Support for multiple language pairs
- **API-First Design**: RESTful API for easy integration with other applications
- **Kubernetes Ready**: Deployment configurations for Kubernetes
- **KServe Integration**: Works with KServe InferenceServices for ML model serving

## Project Structure

```
neural-babel/
├── k8s/                    # Kubernetes deployment configurations
├── scripts/                # Scripts for various operations
│   └── testing/            # Scripts for testing
│       ├── audio/          # Audio files used for testing
│       └── scripts/        # Scripts for testing
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
2. Virtual environment (required)
3. Access to KServe InferenceServices:
   - kube-whisperer (ASR)
   - translation-service
   - vox-raga (TTS)

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
   venv/bin/pip install -r requirements.txt
   ```

4. Configure service endpoints in `.env` file:
   ```
   # Service endpoints (KServe InferenceServices)
   ASR_SERVICE_ENDPOINT=http://kube-whisperer.default.74.224.102.71.nip.io
   TRANSLATION_SERVICE_ENDPOINT=http://translation-service.default.74.224.102.71.nip.io
   TTS_SERVICE_ENDPOINT=http://vox-raga.default.74.224.102.71.nip.io
   
   # Default languages
   DEFAULT_SOURCE_LANG=en
   DEFAULT_TARGET_LANG=fr
   
   # Application configuration
   LOG_LEVEL=INFO
   PORT=8005
   ```

### Running the Services

To run the NeuralBabel orchestrator:

```bash
venv/bin/python -m src.main
```

This will start the service at http://localhost:8005

### Testing the Pipeline

To test the complete speech-to-speech translation pipeline:

```bash
# Run the test script (makes sure your virtual environment is activated)
source venv/bin/activate && ./scripts/testing/run_test.sh
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

## Deployment to Kubernetes

NeuralBabel is designed to work with KServe InferenceServices for the ASR, Translation, and TTS components.

### 1. Build and Push Docker Image

```bash
# Build the image
docker build -t your-registry/neural-babel:latest .

# Push to your registry
docker push your-registry/neural-babel:latest
```

### 2. Update Kubernetes Deployment

Edit the `k8s/deployment.yaml` file to use your image:

```yaml
image: your-registry/neural-babel:latest
```

### 3. Choose Networking Configuration

NeuralBabel supports two networking options for exposing the service:

#### Option A: Standard Kubernetes Ingress (non-Istio environments)

Use the included `ingress.yaml` for standard Kubernetes clusters:

```bash
# Update the host in ingress.yaml
sed -i 's/neural-babel.default.74.224.102.71.nip.io/neural-babel.default.<YOUR-EXTERNAL-IP>.nip.io/g' k8s/ingress.yaml

# Apply Ingress resource
kubectl apply -f k8s/ingress.yaml
```

#### Option B: Istio VirtualService (for Istio/Knative environments)

If your cluster uses Istio or KServe with Knative, use the VirtualService resource:

```bash
# Update the host in virtualservice.yaml
sed -i 's/neural-babel.default.74.224.102.71.nip.io/neural-babel.default.<YOUR-EXTERNAL-IP>.nip.io/g' k8s/virtualservice.yaml

# Apply VirtualService resource
kubectl apply -f k8s/virtualservice.yaml
```

The included `virtualservice.yaml` connects with the standard Knative gateways.

### 4. Deploy to Kubernetes

```bash
# Set your KUBECONFIG if needed
export KUBECONFIG=/path/to/your/kubeconfig

# Apply ConfigMap with service endpoints
kubectl apply -f k8s/configmap.yaml

# Apply Deployment and Service resources
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Apply networking (either Ingress or VirtualService)
kubectl apply -f k8s/virtualservice.yaml  # For Istio environments
# OR
kubectl apply -f k8s/ingress.yaml         # For standard Kubernetes
```

### 5. Verify Deployment

```bash
# Check pods
kubectl get pods -l app=neural-babel

# Check service
kubectl get svc neural-babel

# Check VirtualService (for Istio)
kubectl get virtualservice neural-babel
# OR
# Check Ingress (for standard Kubernetes)
kubectl get ingress neural-babel-ingress
```

After deployment, your service should be accessible at:
```
http://neural-babel.default.<YOUR-EXTERNAL-IP>.nip.io
```

## Testing the Deployed Service

Once NeuralBabel is deployed to your Kubernetes cluster, you can test it using the following methods:

### 1. Testing with curl

Verify your service setup:

```bash
# Define your service URL
SERVICE_URL="http://neural-babel.default.74.224.102.71.nip.io"

# Health check
curl -s $SERVICE_URL/health

# Languages supported
curl -s $SERVICE_URL/languages

# Translating an audio file
curl -X POST \
  -F "audio=@scripts/testing/audio/sample1.wav" \
  -F "source_lang=en" \
  -F "target_lang=fr" \
  -F "audio_format=wav" \
  -F "voice=default" \
  $SERVICE_URL/translate \
  -o translated_audio.wav
```

### 2. Using the Test Script

There is a script in the `scripts/testing` directory that will test the deployed service. Assuming you have the KUBECONFIG set, set the SERVICE_URL to the ingress address and run the script.

```bash
./scripts/testing/test_deployed.sh
```

### 3. Monitoring the Service

To monitor the service and check logs:

```bash
# Get pod name
export KUBECONFIG=/path/to/your/kubeconfig
POD_NAME=$(kubectl get pods -l app=neural-babel -o jsonpath="{.items[0].metadata.name}")

# View logs
kubectl logs $POD_NAME

# Follow logs in real-time
kubectl logs -f $POD_NAME
```

This will help you troubleshoot any issues with the deployed service.