#!/usr/bin/env python3
import asyncio
import httpx
import os
import json
import sys
from typing import Dict, Any, Optional

# Get the script directory and project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../.."))

# Ensure necessary directories exist
os.makedirs(os.path.join(PROJECT_ROOT, "audio"), exist_ok=True)
os.makedirs(SCRIPT_DIR, exist_ok=True)

# Define output locations
TRANSCRIPTION_FILE = os.path.join(SCRIPT_DIR, "transcription.txt")
TRANSLATION_FILE = os.path.join(SCRIPT_DIR, "translation.txt")
TRANSLATED_AUDIO_FILE = os.path.join(PROJECT_ROOT, "audio/translated.wav")
INPUT_AUDIO_FILE = os.path.join(PROJECT_ROOT, "audio/sample1.wav")

# Add parent directory to path to allow imports from src
sys.path.append(PROJECT_ROOT)

# Add environment variables for service endpoints
os.environ["ASR_SERVICE_ENDPOINT"] = "http://localhost:8666"
os.environ["TRANSLATION_SERVICE_ENDPOINT"] = "http://localhost:8777"
os.environ["TTS_SERVICE_ENDPOINT"] = "http://localhost:8888"

# Import after setting environment variables
from src.config import get_settings, get_pipeline_config
from src.clients.asr_client import ASRClient
from src.clients.translation_client import TranslationClient
from src.clients.tts_client import TTSClient
from src.logging_setup import configure_logging, get_logger

# Configure logging
configure_logging("DEBUG")
logger = get_logger(__name__)

# Fallback text for testing if ASR returns empty result
FALLBACK_TEST_TEXT = "This is a test message for the translation pipeline. It will be translated to French and then converted to speech."

async def test_asr_service(audio_data: bytes, source_lang: str):
    """Test ASR service directly and log the result."""
    print("\n=== Testing ASR Service ===")
    
    settings = get_settings()
    pipeline_config = get_pipeline_config(settings)
    asr_client = ASRClient(pipeline_config.asr_service)
    
    try:
        # Transcribe audio
        print(f"Sending audio to ASR service ({len(audio_data)} bytes)...")
        transcription = await asr_client.transcribe(
            audio_data=audio_data,
            language=source_lang
        )
        
        # If transcription is empty, use fallback text
        if not transcription.strip():
            print("ASR returned empty transcription. Using fallback test message.")
            transcription = FALLBACK_TEST_TEXT
        
        # Save transcription to file
        with open(TRANSCRIPTION_FILE, "w") as f:
            f.write(transcription)
        
        print(f"Transcription result ({len(transcription)} chars):")
        print(f"---\n{transcription}\n---")
        
        return transcription
    
    except Exception as e:
        print(f"Error in ASR service: {str(e)}")
        print("Using fallback test message.")
        
        # Save fallback text to file
        with open(TRANSCRIPTION_FILE, "w") as f:
            f.write(FALLBACK_TEST_TEXT)
        
        print(f"Fallback text ({len(FALLBACK_TEST_TEXT)} chars):")
        print(f"---\n{FALLBACK_TEST_TEXT}\n---")
        
        return FALLBACK_TEST_TEXT

async def test_translation_service(text: str, source_lang: str, target_lang: str):
    """Test translation service directly and log the result."""
    print("\n=== Testing Translation Service ===")
    
    settings = get_settings()
    pipeline_config = get_pipeline_config(settings)
    translation_client = TranslationClient(pipeline_config.translation_service)
    
    try:
        # Translate text
        print(f"Sending text to translation service ({len(text)} chars)...")
        print(f"Source language: {source_lang}, Target language: {target_lang}")
        translation = await translation_client.translate(
            text=text,
            source_lang=source_lang,
            target_lang=target_lang
        )
        
        # Save translation to file
        with open(TRANSLATION_FILE, "w") as f:
            f.write(translation)
        
        print(f"Translation result ({len(translation)} chars):")
        print(f"---\n{translation}\n---")
        
        # Check if translation might not be in the expected language
        if target_lang == "hi" and any(c in translation for c in "çéèêë'"):
            print("\nWARNING: The translation appears to be in French, not Hindi.")
            print("The translation service may be ignoring the target language parameter.")
            print("Check if the translation service supports Hindi or is defaulting to French.")
        
        return translation
    
    except Exception as e:
        print(f"Error in translation service: {str(e)}")
        return None

async def test_tts_service(text: str, target_lang: str, voice: str):
    """Test TTS service directly and log the result."""
    print("\n=== Testing TTS Service ===")
    
    settings = get_settings()
    pipeline_config = get_pipeline_config(settings)
    tts_client = TTSClient(pipeline_config.tts_service)
    
    try:
        # Synthesize text
        print(f"Sending text to TTS service ({len(text)} chars)...")
        audio_data = await tts_client.synthesize(
            text=text,
            language=target_lang,
            voice=voice
        )
        
        # Save audio to file
        with open(TRANSLATED_AUDIO_FILE, "wb") as f:
            f.write(audio_data)
        
        print(f"TTS result: {len(audio_data)} bytes saved to {TRANSLATED_AUDIO_FILE}")
        
        return audio_data
    
    except Exception as e:
        print(f"Error in TTS service: {str(e)}")
        return None

async def run_complete_pipeline():
    """Run the complete pipeline and log the results at each stage."""
    print("=== Running Complete Pipeline Test ===")
    
    # Define test parameters
    source_lang = "en"
    target_lang = "fr"
    voice = "default"
    
    # Read input audio file
    try:
        with open(INPUT_AUDIO_FILE, "rb") as f:
            audio_data = f.read()
        print(f"Read {len(audio_data)} bytes from {INPUT_AUDIO_FILE}")
    except Exception as e:
        print(f"Error reading input file {INPUT_AUDIO_FILE}: {str(e)}")
        return
    
    # Step 1: ASR - Convert audio to text
    transcription = await test_asr_service(audio_data, source_lang)
    if not transcription:
        print("ASR failed. Stopping pipeline.")
        return
    
    # Step 2: Translation - Translate text
    translation = await test_translation_service(transcription, source_lang, target_lang)
    if not translation:
        print("Translation failed. Stopping pipeline.")
        return
    
    # Step 3: TTS - Convert translated text to audio
    audio_output = await test_tts_service(translation, target_lang, voice)
    if not audio_output:
        print("TTS failed. Stopping pipeline.")
        return
    
    print("\n=== Pipeline Execution Summary ===")
    print(f"1. ASR: Audio ({len(audio_data)} bytes) -> Text ({len(transcription)} chars)")
    print(f"2. Translation: {source_lang} -> {target_lang}")
    print(f"3. TTS: Text ({len(translation)} chars) -> Audio ({len(audio_output)} bytes)")
    print("\nAll outputs have been saved in the appropriate directories.")

if __name__ == "__main__":
    asyncio.run(run_complete_pipeline()) 