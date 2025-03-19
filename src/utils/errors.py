from typing import Dict, Any, Optional


class NeuralBabelError(Exception):
    """Base exception for all NeuralBabel errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ServiceError(NeuralBabelError):
    """Exception raised when a service call fails."""
    
    def __init__(
        self, 
        message: str, 
        service_name: str, 
        status_code: Optional[int] = None, 
        details: Optional[Dict[str, Any]] = None
    ):
        self.service_name = service_name
        self.status_code = status_code
        super().__init__(message, details)


class ASRError(ServiceError):
    """Exception raised when the ASR service call fails."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None, 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "asr", status_code, details)


class TranslationError(ServiceError):
    """Exception raised when the Translation service call fails."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None, 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "translation", status_code, details)


class TTSError(ServiceError):
    """Exception raised when the TTS service call fails."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None, 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "tts", status_code, details)


class PipelineError(NeuralBabelError):
    """Exception raised when the translation pipeline fails."""
    
    def __init__(
        self, 
        message: str, 
        stage: Optional[str] = None, 
        details: Optional[Dict[str, Any]] = None
    ):
        self.stage = stage
        super().__init__(message, details)


class ConfigurationError(NeuralBabelError):
    """Exception raised when there is a configuration error."""
    pass


class ValidationError(NeuralBabelError):
    """Exception raised when there is a validation error."""
    pass


class ServiceDiscoveryError(NeuralBabelError):
    """Exception raised when service discovery fails."""
    
    def __init__(
        self, 
        message: str, 
        service_name: str, 
        namespace: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        self.service_name = service_name
        self.namespace = namespace
        super().__init__(message, details)
