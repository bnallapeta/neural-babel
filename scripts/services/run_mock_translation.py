import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
import argparse

# Create Translation app
app = FastAPI(title="Mock Translation Service")

class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/translate")
async def translate(request: TranslationRequest):
    # Simulate processing time
    await asyncio.sleep(0.5)
    
    # Return mock translation
    return {"translation": f"This is a mock translation of '{request.text}' from {request.source_lang} to {request.target_lang}."}

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run mock Translation service")
    parser.add_argument("--port", type=int, default=8002, help="Port to run the service on")
    args = parser.parse_args()
    
    # Run the service
    uvicorn.run(app, host="0.0.0.0", port=args.port) 