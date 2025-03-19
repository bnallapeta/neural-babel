import uvicorn
from fastapi import FastAPI, File, Form
from fastapi.responses import JSONResponse
import asyncio
import argparse

# Create ASR app
app = FastAPI(title="Mock ASR Service")

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/transcribe")
async def transcribe(audio: bytes = File(...), language: str = Form(...), audio_format: str = Form("wav")):
    # Simulate processing time
    await asyncio.sleep(0.5)
    
    # Return mock transcription
    return {"text": "This is a mock transcription for testing purposes."}

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run mock ASR service")
    parser.add_argument("--port", type=int, default=8001, help="Port to run the service on")
    args = parser.parse_args()
    
    # Run the service
    uvicorn.run(app, host="0.0.0.0", port=args.port) 