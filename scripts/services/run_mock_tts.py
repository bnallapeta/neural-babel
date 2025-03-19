import uvicorn
from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
import asyncio
import random
import string
import argparse

# Create TTS app
app = FastAPI(title="Mock TTS Service")

class TTSRequest(BaseModel):
    text: str
    language: str
    voice: str = "default"
    audio_format: str = "wav"

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/synthesize")
async def synthesize(request: TTSRequest):
    # Simulate processing time
    await asyncio.sleep(0.5)
    
    # Generate random audio data (just for testing)
    mock_audio_data = bytes(''.join(random.choices(string.ascii_letters, k=1000)), 'utf-8')
    
    # Determine content type based on format
    content_type = {
        "wav": "audio/wav",
        "mp3": "audio/mpeg",
        "ogg": "audio/ogg"
    }.get(request.audio_format, "application/octet-stream")
    
    return Response(content=mock_audio_data, media_type=content_type)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run mock TTS service")
    parser.add_argument("--port", type=int, default=8003, help="Port to run the service on")
    args = parser.parse_args()
    
    # Run the service
    uvicorn.run(app, host="0.0.0.0", port=args.port) 