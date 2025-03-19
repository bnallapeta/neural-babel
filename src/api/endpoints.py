import io
import time
import asyncio
import os
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from src.config import get_settings, get_pipeline_config
from src.orchestrator.pipeline import get_pipeline, TranslationPipeline
from src.api.models import (
    TranslationRequest,
    HealthResponse,
    LanguagePair,
    LanguagesResponse,
    ConfigResponse,
    ErrorResponse,
    get_language_name
)
from src.utils.errors import PipelineError
from src.utils.metrics import (
    SYSTEM_MEMORY_USAGE,
    SYSTEM_CPU_USAGE
)
from src.logging_setup import get_logger

# Create router
router = APIRouter()

# Get logger
logger = get_logger(__name__)

# Get settings
settings = get_settings()

# Get pipeline config
pipeline_config = get_pipeline_config(settings)

# Create pipeline
pipeline = get_pipeline(pipeline_config)


# Health check endpoint
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check the health of the service.
    """
    try:
        # Check component services health
        services_health = await pipeline.check_services_health()
        
        # Determine overall status
        if all(services_health.values()):
            status = "ok"
        elif any(services_health.values()):
            status = "degraded"
        else:
            status = "error"
        
        # Get version from environment or default
        version = os.environ.get("VERSION", "0.1.0")
        
        # Return health response
        return HealthResponse(
            status=status,
            version=version,
            services=services_health
        )
    except Exception as e:
        logger.error("Health check failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


# Readiness check endpoint
@router.get("/ready")
async def readiness_check():
    """
    Check if the service is ready to handle requests.
    """
    try:
        # Check component services health
        services_health = await pipeline.check_services_health()
        
        # If any service is healthy, we're ready
        if any(services_health.values()):
            return {"status": "ready"}
        else:
            raise HTTPException(
                status_code=503,
                detail="Service is not ready: no component services are healthy"
            )
    except Exception as e:
        logger.error("Readiness check failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=503,
            detail=f"Service is not ready: {str(e)}"
        )


# Liveness check endpoint
@router.get("/live")
async def liveness_check():
    """
    Check if the service is alive.
    """
    return {"status": "alive"}


# Metrics endpoint
@router.get("/metrics")
async def metrics():
    """
    Get Prometheus metrics.
    """
    # Update system metrics
    try:
        import psutil
        
        # Update memory usage
        memory = psutil.virtual_memory()
        SYSTEM_MEMORY_USAGE.set(memory.used)
        
        # Update CPU usage
        SYSTEM_CPU_USAGE.set(psutil.cpu_percent())
    except ImportError:
        # psutil not available
        pass
    
    # Generate metrics
    return StreamingResponse(
        io.BytesIO(generate_latest()),
        media_type=CONTENT_TYPE_LATEST
    )


# Configuration endpoint
@router.get("/config", response_model=ConfigResponse)
async def get_config():
    """
    Get the current configuration.
    """
    return ConfigResponse(
        asr_service=pipeline_config.asr_service.name,
        translation_service=pipeline_config.translation_service.name,
        tts_service=pipeline_config.tts_service.name,
        default_source_lang=pipeline_config.default_source_lang,
        default_target_lang=pipeline_config.default_target_lang,
        enable_streaming=pipeline_config.enable_streaming,
        cache_enabled=pipeline_config.cache_enabled
    )


# Languages endpoint
@router.get("/languages", response_model=LanguagesResponse)
async def get_languages():
    """
    Get available language pairs.
    """
    # Create language pairs
    language_pairs = []
    for source_lang, target_lang in pipeline_config.supported_language_pairs:
        language_pairs.append(
            LanguagePair(
                source_lang=source_lang,
                target_lang=target_lang,
                source_name=get_language_name(source_lang),
                target_name=get_language_name(target_lang)
            )
        )
    
    # Return response
    return LanguagesResponse(
        language_pairs=language_pairs,
        default_source_lang=pipeline_config.default_source_lang,
        default_target_lang=pipeline_config.default_target_lang
    )


# Translation endpoint with form data
@router.post("/translate")
async def translate_speech_form(
    audio: UploadFile = File(...),
    source_lang: str = Form(...),
    target_lang: str = Form(...),
    audio_format: str = Form("wav"),
    voice: str = Form("default"),
    background_tasks: BackgroundTasks = None
):
    """
    Translate speech from source language to target language using form data.
    """
    # Read audio data
    audio_data = await audio.read()
    
    # Call the main translation function
    return await translate_speech_internal(
        audio_data=audio_data,
        source_lang=source_lang,
        target_lang=target_lang,
        audio_format=audio_format,
        voice=voice,
        background_tasks=background_tasks
    )


# Translation endpoint with JSON
@router.post("/translate/json")
async def translate_speech_json(
    request: TranslationRequest,
    background_tasks: BackgroundTasks = None
):
    """
    Translate speech from source language to target language using JSON.
    """
    # Call the main translation function
    return await translate_speech_internal(
        audio_data=request.audio,
        source_lang=request.source_lang,
        target_lang=request.target_lang,
        audio_format=request.audio_format,
        voice=request.voice,
        background_tasks=background_tasks
    )


# Internal translation function
async def translate_speech_internal(
    audio_data: bytes,
    source_lang: str,
    target_lang: str,
    audio_format: str,
    voice: str,
    background_tasks: BackgroundTasks = None
):
    """
    Internal function to translate speech.
    """
    try:
        # Start timing
        start_time = time.time()
        
        # Validate language pair
        valid_pairs = pipeline_config.supported_language_pairs
        if (source_lang, target_lang) not in valid_pairs:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language pair: {source_lang} to {target_lang}"
            )
        
        # Perform translation
        audio_output = await pipeline.translate_speech(
            audio_data=audio_data,
            source_lang=source_lang,
            target_lang=target_lang,
            audio_format=audio_format,
            voice=voice
        )
        
        # Record latency
        latency = time.time() - start_time
        
        # Schedule cleanup if background tasks are available
        if background_tasks:
            background_tasks.add_task(cleanup_resources)
        
        # Determine content type based on format
        content_type = {
            "wav": "audio/wav",
            "mp3": "audio/mpeg",
            "ogg": "audio/ogg"
        }.get(audio_format, "application/octet-stream")
        
        # Return audio stream
        return StreamingResponse(
            io.BytesIO(audio_output),
            media_type=content_type,
            headers={
                "X-Processing-Time": str(latency),
                "X-Source-Language": source_lang,
                "X-Target-Language": target_lang
            }
        )
    except PipelineError as e:
        # Log error
        logger.error(
            "Translation pipeline error",
            error=str(e),
            stage=e.stage,
            details=e.details,
            source_lang=source_lang,
            target_lang=target_lang
        )
        
        # Return error response
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=str(e),
                status_code=500,
                details=e.details,
                stage=e.stage
            ).dict()
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log error
        logger.error(
            "Unexpected error in translation endpoint",
            error=str(e),
            source_lang=source_lang,
            target_lang=target_lang,
            exc_info=True
        )
        
        # Return error response
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=f"Unexpected error: {str(e)}",
                status_code=500
            ).dict()
        )


# Cleanup function
async def cleanup_resources():
    """
    Clean up resources after request.
    """
    # This is a placeholder for any cleanup tasks
    # For example, you might want to clean up temporary files
    pass
