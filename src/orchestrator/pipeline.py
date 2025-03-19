import asyncio
import time
from typing import Dict, Any, Optional

from src.config import PipelineConfig
from src.clients.asr_client import ASRClient
from src.clients.translation_client import TranslationClient
from src.clients.tts_client import TTSClient
from src.logging_setup import get_logger
from src.utils.errors import PipelineError, ASRError, TranslationError, TTSError
from src.utils.metrics import (
    PIPELINE_STAGE_LATENCY,
    PIPELINE_COMPLETION_RATE,
    TRANSLATION_REQUESTS,
    TRANSLATION_ERRORS,
    TRANSLATION_LATENCY
)

logger = get_logger(__name__)


class TranslationPipeline:
    """
    Orchestrates the end-to-end translation pipeline.
    """
    
    def __init__(self, config: PipelineConfig):
        """
        Initialize the translation pipeline.
        
        Args:
            config: Pipeline configuration
        """
        self.config = config
        self.asr_client = ASRClient(config.asr_service)
        self.translation_client = TranslationClient(config.translation_service)
        self.tts_client = TTSClient(config.tts_service)
    
    async def check_services_health(self) -> Dict[str, bool]:
        """
        Check the health of all services.
        
        Returns:
            Dict[str, bool]: Health status of each service
        """
        # Check health of all services in parallel
        asr_health_task = asyncio.create_task(self.asr_client.check_health())
        translation_health_task = asyncio.create_task(self.translation_client.check_health())
        tts_health_task = asyncio.create_task(self.tts_client.check_health())
        
        # Wait for all health checks to complete
        asr_health = await asr_health_task
        translation_health = await translation_health_task
        tts_health = await tts_health_task
        
        # Return health status
        return {
            "asr": asr_health,
            "translation": translation_health,
            "tts": tts_health
        }
    
    async def translate_speech(
        self, 
        audio_data: bytes,
        source_lang: str,
        target_lang: str,
        audio_format: str = "wav",
        voice: str = "default"
    ) -> bytes:
        """
        Perform end-to-end speech translation.
        
        Args:
            audio_data: Raw audio bytes
            source_lang: Source language code
            target_lang: Target language code
            audio_format: Format of input/output audio
            voice: Voice ID for synthesis
            
        Returns:
            bytes: Translated audio as bytes
            
        Raises:
            PipelineError: If the pipeline fails
        """
        # Record start time
        start_time = time.time()
        
        # Increment request counter
        TRANSLATION_REQUESTS.labels(
            source_lang=source_lang,
            target_lang=target_lang
        ).inc()
        
        try:
            # Step 1: Speech-to-Text
            logger.info(
                "Starting ASR",
                source_lang=source_lang,
                audio_format=audio_format,
                audio_size=len(audio_data)
            )
            
            asr_start_time = time.time()
            
            try:
                transcription = await self.asr_client.transcribe(
                    audio_data=audio_data,
                    language=source_lang,
                    audio_format=audio_format
                )
                
                # Record ASR latency
                asr_latency = time.time() - asr_start_time
                PIPELINE_STAGE_LATENCY.labels(stage="asr").observe(asr_latency)
                
                logger.info(
                    "ASR completed",
                    source_lang=source_lang,
                    transcription_length=len(transcription),
                    duration=asr_latency
                )
            except ASRError as e:
                # Record error
                TRANSLATION_ERRORS.labels(
                    type="asr_error",
                    stage="asr"
                ).inc()
                
                # Log error
                logger.error(
                    "ASR failed",
                    error=str(e),
                    source_lang=source_lang,
                    audio_format=audio_format,
                    audio_size=len(audio_data)
                )
                
                # Raise pipeline error
                raise PipelineError(
                    f"ASR failed: {str(e)}",
                    stage="asr",
                    details=e.details
                )
            
            # Step 2: Text Translation
            logger.info(
                "Starting translation",
                source_lang=source_lang,
                target_lang=target_lang,
                text_length=len(transcription)
            )
            
            translation_start_time = time.time()
            
            try:
                translation = await self.translation_client.translate(
                    text=transcription,
                    source_lang=source_lang,
                    target_lang=target_lang
                )
                
                # Record translation latency
                translation_latency = time.time() - translation_start_time
                PIPELINE_STAGE_LATENCY.labels(stage="translation").observe(translation_latency)
                
                logger.info(
                    "Translation completed",
                    source_lang=source_lang,
                    target_lang=target_lang,
                    text_length=len(transcription),
                    translation_length=len(translation),
                    duration=translation_latency
                )
            except TranslationError as e:
                # Record error
                TRANSLATION_ERRORS.labels(
                    type="translation_error",
                    stage="translation"
                ).inc()
                
                # Log error
                logger.error(
                    "Translation failed",
                    error=str(e),
                    source_lang=source_lang,
                    target_lang=target_lang,
                    text_length=len(transcription)
                )
                
                # Raise pipeline error
                raise PipelineError(
                    f"Translation failed: {str(e)}",
                    stage="translation",
                    details=e.details
                )
            
            # Step 3: Text-to-Speech
            logger.info(
                "Starting TTS",
                target_lang=target_lang,
                voice=voice,
                audio_format=audio_format,
                text_length=len(translation)
            )
            
            tts_start_time = time.time()
            
            try:
                audio_output = await self.tts_client.synthesize(
                    text=translation,
                    language=target_lang,
                    voice=voice,
                    audio_format=audio_format
                )
                
                # Record TTS latency
                tts_latency = time.time() - tts_start_time
                PIPELINE_STAGE_LATENCY.labels(stage="tts").observe(tts_latency)
                
                logger.info(
                    "TTS completed",
                    target_lang=target_lang,
                    voice=voice,
                    audio_format=audio_format,
                    text_length=len(translation),
                    audio_size=len(audio_output),
                    duration=tts_latency
                )
            except TTSError as e:
                # Record error
                TRANSLATION_ERRORS.labels(
                    type="tts_error",
                    stage="tts"
                ).inc()
                
                # Log error
                logger.error(
                    "TTS failed",
                    error=str(e),
                    target_lang=target_lang,
                    voice=voice,
                    audio_format=audio_format,
                    text_length=len(translation)
                )
                
                # Raise pipeline error
                raise PipelineError(
                    f"TTS failed: {str(e)}",
                    stage="tts",
                    details=e.details
                )
            
            # Record total latency
            total_latency = time.time() - start_time
            TRANSLATION_LATENCY.labels(
                source_lang=source_lang,
                target_lang=target_lang
            ).observe(total_latency)
            
            # Record success
            PIPELINE_COMPLETION_RATE.labels(status="success").inc()
            
            # Log success
            logger.info(
                "Translation pipeline completed successfully",
                source_lang=source_lang,
                target_lang=target_lang,
                audio_format=audio_format,
                voice=voice,
                input_audio_size=len(audio_data),
                output_audio_size=len(audio_output),
                total_duration=total_latency
            )
            
            return audio_output
            
        except PipelineError:
            # Re-raise pipeline errors
            PIPELINE_COMPLETION_RATE.labels(status="failure").inc()
            raise
            
        except Exception as e:
            # Record error
            TRANSLATION_ERRORS.labels(
                type="unexpected_error",
                stage="pipeline"
            ).inc()
            
            # Record failure
            PIPELINE_COMPLETION_RATE.labels(status="failure").inc()
            
            # Log error
            logger.error(
                "Unexpected error in translation pipeline",
                error=str(e),
                source_lang=source_lang,
                target_lang=target_lang,
                audio_format=audio_format,
                voice=voice,
                exc_info=True
            )
            
            # Raise pipeline error
            raise PipelineError(
                f"Unexpected error in translation pipeline: {str(e)}",
                stage="pipeline",
                details={"error": str(e)}
            )


# Singleton instance
_pipeline = None


def get_pipeline(config: PipelineConfig) -> TranslationPipeline:
    """
    Get the translation pipeline instance.
    
    Args:
        config: Pipeline configuration
        
    Returns:
        TranslationPipeline: Translation pipeline instance
    """
    global _pipeline
    if _pipeline is None:
        _pipeline = TranslationPipeline(config)
    return _pipeline
