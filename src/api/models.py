from typing import List, Dict, Optional, Tuple, Any
from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    """
    Request model for speech translation.
    """
    audio: bytes = Field(..., description="Audio data as bytes")
    source_lang: str = Field(..., description="Source language code")
    target_lang: str = Field(..., description="Target language code")
    audio_format: str = Field("wav", description="Audio format (wav, mp3, ogg)")
    voice: str = Field("default", description="Voice ID for synthesis")


class HealthResponse(BaseModel):
    """
    Response model for health check.
    """
    status: str = Field(..., description="Health status (ok, degraded, error)")
    version: str = Field(..., description="Service version")
    services: Dict[str, bool] = Field(..., description="Health status of component services")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional health details")


class LanguagePair(BaseModel):
    """
    Model for a language pair.
    """
    source_lang: str = Field(..., description="Source language code")
    target_lang: str = Field(..., description="Target language code")
    source_name: str = Field(..., description="Source language name")
    target_name: str = Field(..., description="Target language name")


class LanguagesResponse(BaseModel):
    """
    Response model for available language pairs.
    """
    language_pairs: List[LanguagePair] = Field(..., description="Available language pairs")
    default_source_lang: str = Field(..., description="Default source language code")
    default_target_lang: str = Field(..., description="Default target language code")


class ConfigResponse(BaseModel):
    """
    Response model for configuration.
    """
    asr_service: str = Field(..., description="ASR service name")
    translation_service: str = Field(..., description="Translation service name")
    tts_service: str = Field(..., description="TTS service name")
    default_source_lang: str = Field(..., description="Default source language code")
    default_target_lang: str = Field(..., description="Default target language code")
    enable_streaming: bool = Field(..., description="Whether streaming is enabled")
    cache_enabled: bool = Field(..., description="Whether caching is enabled")


class ErrorResponse(BaseModel):
    """
    Response model for errors.
    """
    error: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    stage: Optional[str] = Field(None, description="Pipeline stage where the error occurred")


# Language name mapping
LANGUAGE_NAMES = {
    "en": "English",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "nl": "Dutch",
    "ru": "Russian",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "hi": "Hindi",
    "bn": "Bengali",
    "ur": "Urdu",
    "tr": "Turkish",
    "fa": "Persian",
    "sw": "Swahili",
    "vi": "Vietnamese",
    "th": "Thai"
}


def get_language_name(lang_code: str) -> str:
    """
    Get the language name for a language code.
    
    Args:
        lang_code: Language code
        
    Returns:
        str: Language name
    """
    return LANGUAGE_NAMES.get(lang_code, lang_code)
