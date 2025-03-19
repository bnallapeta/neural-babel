from typing import List, Optional, Tuple
import os
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class ServiceConfig(BaseModel):
    """Configuration for a component service."""
    name: str
    namespace: str = "default"
    service_type: str  # "asr", "translation", "tts"
    endpoint: Optional[str] = None  # If None, will use service discovery
    timeout: float = 30.0
    retries: int = 3
    backoff_factor: float = 0.5


class PipelineConfig(BaseModel):
    """Configuration for the translation pipeline."""
    asr_service: ServiceConfig
    translation_service: ServiceConfig
    tts_service: ServiceConfig
    default_source_lang: str = "en"
    default_target_lang: str = "fr"
    supported_language_pairs: List[Tuple[str, str]] = [
        ("en", "fr"), ("en", "de"), ("en", "hi"),
        ("fr", "en"), ("de", "en"), ("hi", "en")
    ]
    enable_streaming: bool = False
    cache_enabled: bool = True
    cache_ttl: int = 3600  # seconds


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    # Service names and namespaces
    asr_service_name: str = "kube-whisperer"
    asr_service_namespace: str = "default"
    translation_service_name: str = "lexi-shift"
    translation_service_namespace: str = "default"
    tts_service_name: str = "vox-raga"
    tts_service_namespace: str = "default"
    
    # Service endpoints for local development
    asr_service_endpoint: Optional[str] = None
    translation_service_endpoint: Optional[str] = None
    tts_service_endpoint: Optional[str] = None
    
    # Default languages
    default_source_lang: str = "en"
    default_target_lang: str = "fr"
    
    # Service configuration
    service_timeout: float = 30.0
    service_retries: int = 3
    service_backoff_factor: float = 0.5
    
    # Pipeline configuration
    enable_streaming: bool = False
    cache_enabled: bool = True
    cache_ttl: int = 3600  # seconds
    
    # Application configuration
    log_level: str = "INFO"
    port: Optional[int] = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


def get_pipeline_config(settings: Settings = None) -> PipelineConfig:
    """
    Create a PipelineConfig from application settings.
    
    Args:
        settings: Application settings. If None, will load from environment.
        
    Returns:
        PipelineConfig: Configuration for the translation pipeline.
    """
    if settings is None:
        settings = get_settings()
    
    # Create service configurations
    asr_service = ServiceConfig(
        name=settings.asr_service_name,
        namespace=settings.asr_service_namespace,
        service_type="asr",
        endpoint=settings.asr_service_endpoint,
        timeout=settings.service_timeout,
        retries=settings.service_retries,
        backoff_factor=settings.service_backoff_factor
    )
    
    translation_service = ServiceConfig(
        name=settings.translation_service_name,
        namespace=settings.translation_service_namespace,
        service_type="translation",
        endpoint=settings.translation_service_endpoint,
        timeout=settings.service_timeout,
        retries=settings.service_retries,
        backoff_factor=settings.service_backoff_factor
    )
    
    tts_service = ServiceConfig(
        name=settings.tts_service_name,
        namespace=settings.tts_service_namespace,
        service_type="tts",
        endpoint=settings.tts_service_endpoint,
        timeout=settings.service_timeout,
        retries=settings.service_retries,
        backoff_factor=settings.service_backoff_factor
    )
    
    # Create pipeline configuration
    return PipelineConfig(
        asr_service=asr_service,
        translation_service=translation_service,
        tts_service=tts_service,
        default_source_lang=settings.default_source_lang,
        default_target_lang=settings.default_target_lang,
        enable_streaming=settings.enable_streaming,
        cache_enabled=settings.cache_enabled,
        cache_ttl=settings.cache_ttl
    )
