import asyncio
import time
from typing import Dict, Any, Optional

import httpx
from httpx import Response

from src.config import ServiceConfig
from src.logging_setup import get_logger
from src.orchestrator.service_discovery import get_service_discovery
from src.utils.errors import TTSError
from src.utils.metrics import SERVICE_REQUESTS, SERVICE_ERRORS, SERVICE_LATENCY

logger = get_logger(__name__)


class TTSClient:
    """
    Client for the Vox-Raga TTS service.
    """
    
    def __init__(self, service_config: ServiceConfig):
        """
        Initialize the TTS client.
        
        Args:
            service_config: Service configuration
        """
        self.service_config = service_config
        self.service_discovery = get_service_discovery()
        self.base_url = None
    
    async def _get_base_url(self) -> str:
        """
        Get the base URL for the TTS service.
        
        Returns:
            str: Base URL
        """
        if self.base_url is None:
            self.base_url = self.service_discovery.get_service_url(self.service_config)
        return self.base_url
    
    async def _make_request(
        self, 
        method: str, 
        path: str, 
        **kwargs
    ) -> Response:
        """
        Make a request to the TTS service.
        
        Args:
            method: HTTP method
            path: Request path
            **kwargs: Additional arguments for the request
            
        Returns:
            Response: HTTP response
            
        Raises:
            TTSError: If the request fails
        """
        # Get base URL
        base_url = await self._get_base_url()
        
        # Construct URL
        url = f"{base_url}{path}"
        
        # Set timeout
        timeout = httpx.Timeout(self.service_config.timeout)
        
        # Initialize retry count
        retry_count = 0
        
        while True:
            try:
                # Record start time
                start_time = time.time()
                
                # Increment request counter
                SERVICE_REQUESTS.labels(
                    service="tts",
                    operation=path
                ).inc()
                
                # Make request
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.request(
                        method=method,
                        url=url,
                        **kwargs
                    )
                
                # Record latency
                latency = time.time() - start_time
                SERVICE_LATENCY.labels(
                    service="tts",
                    operation=path
                ).observe(latency)
                
                # Check response
                if response.status_code >= 400:
                    # Increment error counter
                    SERVICE_ERRORS.labels(
                        service="tts",
                        operation=path,
                        error_type=f"http_{response.status_code}"
                    ).inc()
                    
                    # Log error
                    logger.error(
                        "TTS service request failed",
                        status_code=response.status_code,
                        response=response.text,
                        url=url
                    )
                    
                    # Raise error
                    raise TTSError(
                        f"TTS service request failed with status code {response.status_code}: {response.text}",
                        response.status_code,
                        {"response": response.text}
                    )
                
                # Return response
                return response
            
            except httpx.TimeoutException as e:
                # Increment error counter
                SERVICE_ERRORS.labels(
                    service="tts",
                    operation=path,
                    error_type="timeout"
                ).inc()
                
                # Log error
                logger.warning(
                    "TTS service request timed out",
                    retry_count=retry_count,
                    max_retries=self.service_config.retries,
                    url=url
                )
                
                # Check if we should retry
                if retry_count < self.service_config.retries:
                    # Increment retry count
                    retry_count += 1
                    
                    # Calculate backoff time
                    backoff_time = self.service_config.backoff_factor * (2 ** (retry_count - 1))
                    
                    # Log retry
                    logger.info(
                        "Retrying TTS service request",
                        retry_count=retry_count,
                        backoff_time=backoff_time,
                        url=url
                    )
                    
                    # Wait before retrying
                    await asyncio.sleep(backoff_time)
                    
                    # Continue to next retry
                    continue
                
                # If we've exhausted retries, raise error
                raise TTSError(
                    f"TTS service request timed out after {retry_count} retries: {str(e)}",
                    None,
                    {"error": str(e)}
                )
            
            except Exception as e:
                # Increment error counter
                SERVICE_ERRORS.labels(
                    service="tts",
                    operation=path,
                    error_type=type(e).__name__
                ).inc()
                
                # Log error
                logger.error(
                    "TTS service request failed",
                    error=str(e),
                    url=url,
                    exc_info=True
                )
                
                # Raise error
                raise TTSError(
                    f"TTS service request failed: {str(e)}",
                    None,
                    {"error": str(e)}
                )
    
    async def synthesize(
        self, 
        text: str, 
        language: str,
        voice: str = "default",
        audio_format: str = "wav"
    ) -> bytes:
        """
        Synthesize text to speech.
        
        Args:
            text: Text to synthesize
            language: Language code
            voice: Voice ID
            audio_format: Audio format
            
        Returns:
            bytes: Audio data
            
        Raises:
            TTSError: If synthesis fails
        """
        try:
            # Prepare request
            json_data = {
                "text": text,
                "language": language,
                "voice": voice,
                "audio_format": audio_format
            }
            
            # Make request
            response = await self._make_request(
                method="POST",
                path="/synthesize",
                json=json_data
            )
            
            # Get audio data
            audio_data = response.content
            
            # Log success
            logger.info(
                "Text synthesized successfully",
                language=language,
                voice=voice,
                audio_format=audio_format,
                text_length=len(text),
                audio_size=len(audio_data)
            )
            
            return audio_data
        
        except TTSError:
            # Re-raise TTS errors
            raise
        
        except Exception as e:
            # Log error
            logger.error(
                "Synthesis failed",
                error=str(e),
                language=language,
                voice=voice,
                audio_format=audio_format,
                text_length=len(text),
                exc_info=True
            )
            
            # Raise error
            raise TTSError(
                f"Synthesis failed: {str(e)}",
                None,
                {
                    "error": str(e),
                    "language": language,
                    "voice": voice,
                    "audio_format": audio_format,
                    "text_length": len(text)
                }
            )
    
    async def check_health(self) -> bool:
        """
        Check if the TTS service is healthy.
        
        Returns:
            bool: True if the service is healthy, False otherwise
        """
        return await self.service_discovery.check_service_health(self.service_config)
