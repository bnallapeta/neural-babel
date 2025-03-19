import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
import random
import string
from typing import Dict, Any, Optional

# Create ASR app
asr_app = FastAPI(title="Mock ASR Service")

@asr_app.get("/health")
async def asr_health():
    return {"status": "healthy"}

@asr_app.post("/transcribe")
async def transcribe(audio: bytes = File(...), language: str = Form(...), audio_format: str = Form("wav")):
    # Simulate processing time
    await asyncio.sleep(0.5)
    
    # Return mock transcription
    return {"text": "This is a mock transcription for testing purposes."}

# Create Translation app
translation_app = FastAPI(title="Mock Translation Service")

class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str

@translation_app.get("/health")
async def translation_health():
    return {"status": "healthy"}

@translation_app.post("/translate")
async def translate(request: TranslationRequest):
    # Simulate processing time
    await asyncio.sleep(0.5)
    
    # Return mock translation
    return {"translation": f"This is a mock translation of '{request.text}' from {request.source_lang} to {request.target_lang}."}

# Create TTS app
tts_app = FastAPI(title="Mock TTS Service")

class TTSRequest(BaseModel):
    text: str
    language: str
    voice: str = "default"
    audio_format: str = "wav"

@tts_app.get("/health")
async def tts_health():
    return {"status": "healthy"}

@tts_app.post("/synthesize")
async def synthesize(request: TTSRequest):
    # Simulate processing time
    await asyncio.sleep(0.5)
    
    # Generate random audio data (just for testing)
    mock_audio_data = bytes(''.join(random.choices(string.ascii_letters, k=1000)), 'utf-8')
    
    return mock_audio_data

# Run the services
def run_asr_service():
    uvicorn.run(asr_app, host="0.0.0.0", port=8001)

def run_translation_service():
    uvicorn.run(translation_app, host="0.0.0.0", port=8002)

def run_tts_service():
    uvicorn.run(tts_app, host="0.0.0.0", port=8003)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run mock services for NeuralBabel testing")
    parser.add_argument("service", choices=["asr", "translation", "tts", "all"], help="Service to run")
    
    args = parser.parse_args()
    
    if args.service == "asr":
        run_asr_service()
    elif args.service == "translation":
        run_translation_service()
    elif args.service == "tts":
        run_tts_service()
    elif args.service == "all":
        # This won't work well in a single process, but we'll include it for completeness
        print("Running all services is not supported in a single process. Please run each service separately.")
        print("Run the following commands in separate terminals:")
        print("python mock_services.py asr")
        print("python mock_services.py translation")
        print("python mock_services.py tts") 