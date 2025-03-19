# Running NeuralBabel and Its Services

This README explains how to run the NeuralBabel system and its component services.

## Option 1: Running Mock Services (for development and testing)

For quick development and testing, you can run the mock services:

```bash
# Run all mock services and NeuralBabel in a single command
./run_services_mock.sh
```

This will start:
- Mock ASR service on port 8001
- Mock Translation service on port 8002
- Mock TTS service on port 8003
- NeuralBabel on port 8005

## Option 2: Running Real Services (recommended for full functionality)

For a complete setup with real services, open 4 separate terminal windows and run each service individually:

### Terminal 1: ASR Service (Whisper)
```bash
./run_asr.sh
```

### Terminal 2: Translation Service (Lexi-Shift)
```bash
./run_translation.sh
```

### Terminal 3: TTS Service (Vox-Raga)
```bash
./run_tts.sh
```

### Terminal 4: NeuralBabel
```bash
./run_neural_babel.sh
```

This approach provides several advantages:
1. Each service runs in its own terminal window, making it easier to view logs
2. You can start/stop individual services as needed
3. Virtual environment issues are avoided by running each in a dedicated terminal
4. Proper dependency separation is maintained

## Testing the Services

Once all services are running, you can test the complete system:

```bash
# Generate test audio if needed
python generate_test_audio.py

# Test the translation endpoint
curl -s -X POST -F "audio=@test_audio.wav" -F "source_lang=en" -F "target_lang=fr" -F "audio_format=wav" -F "voice=default" http://localhost:8005/translate -o response_audio.wav
```

Additional endpoints:
- Health check: `curl -s http://localhost:8005/health`
- Languages: `curl -s http://localhost:8005/languages`
- Configuration: `curl -s http://localhost:8005/config`

## Troubleshooting

If you encounter issues with dependencies in the real services:
1. Navigate to each service's directory
2. Activate its virtual environment: `source venv/bin/activate`
3. Install missing dependencies: `pip install psutil structlog python-dotenv httpx`
4. Then try running the service again 