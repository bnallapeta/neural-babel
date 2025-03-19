#!/usr/bin/env python3
import asyncio
import httpx
import sys
import os
from typing import Dict, Any, Optional

# Add environment variables for service endpoints
os.environ["ASR_SERVICE_ENDPOINT"] = "http://localhost:8666"
os.environ["TRANSLATION_SERVICE_ENDPOINT"] = "http://localhost:8777"
os.environ["TTS_SERVICE_ENDPOINT"] = "http://localhost:8888"

# Import after setting environment variables
from src.config import get_settings, get_pipeline_config
from src.orchestrator.pipeline import TranslationPipeline
from src.logging_setup import configure_logging, get_logger

# Configure logging
configure_logging("DEBUG")
logger = get_logger(__name__)

async def test_health_check():
    """Test health checks for all services."""
    print("\n=== Testing Service Health Checks ===")
    
    # Get settings and create pipeline config
    settings = get_settings()
    pipeline_config = get_pipeline_config(settings)
    
    # Print service endpoints
    print(f"ASR Service: {pipeline_config.asr_service.endpoint}")
    print(f"Translation Service: {pipeline_config.translation_service.endpoint}")
    print(f"TTS Service: {pipeline_config.tts_service.endpoint}")
    
    # Create pipeline
    pipeline = TranslationPipeline(pipeline_config)
    
    # Check services health
    health_status = await pipeline.check_services_health()
    
    # Print health status
    print("\nHealth Status:")
    for service, status in health_status.items():
        status_str = "✅ HEALTHY" if status else "❌ UNHEALTHY"
        print(f"{service}: {status_str}")
    
    return all(health_status.values())

async def test_translation():
    """Test the full translation pipeline."""
    print("\n=== Testing Translation Pipeline ===")
    
    # Get settings and create pipeline config
    settings = get_settings()
    pipeline_config = get_pipeline_config(settings)
    
    # Create pipeline
    pipeline = TranslationPipeline(pipeline_config)
    
    # Check if test audio file exists
    if not os.path.exists("test_audio.wav"):
        print("Error: test_audio.wav not found. Please create a test audio file.")
        return False
    
    try:
        # Read audio file
        with open("test_audio.wav", "rb") as f:
            audio_data = f.read()
        
        print(f"Read {len(audio_data)} bytes from test_audio.wav")
        
        # Define source and target language
        source_lang = "en"
        target_lang = "fr"
        voice = "default"
        audio_format = "wav"
        
        # Perform translation
        print(f"Translating from {source_lang} to {target_lang}...")
        result = await pipeline.translate_speech(
            audio_data=audio_data,
            source_lang=source_lang,
            target_lang=target_lang,
            voice=voice,
            audio_format=audio_format
        )
        
        # Save result
        output_file = "response_direct.wav"
        with open(output_file, "wb") as f:
            f.write(result)
        
        print(f"Translation successful! Saved to {output_file}")
        return True
    
    except Exception as e:
        print(f"Error in translation pipeline: {str(e)}")
        return False

async def main():
    """Run all tests."""
    # Test health check
    health_ok = await test_health_check()
    
    if health_ok:
        # Test translation
        await test_translation()
    else:
        print("\nSkipping translation test due to health check failures.")

if __name__ == "__main__":
    asyncio.run(main()) 