import asyncio
import time
from typing import Dict, Any, Optional

import httpx
from httpx import Response

from src.config import ServiceConfig
from src.logging_setup import get_logger
from src.orchestrator.service_discovery import get_service_discovery
from src.utils.errors import ASRError
from src.utils.metrics import SERVICE_REQUESTS, SERVICE_ERRORS, SERVICE_LATENCY

logger = get_logger(__name__)


class ASRClient:
    """
    Client for the Kube-Whisperer ASR service.
    """
    
    def __init__(self, service_config: ServiceConfig):
        """
        Initialize the ASR client.
        
        Args:
            service_config: Service configuration
        """
        self.service_config = service_config
        self.service_discovery = get_service_discovery()
        self.base_url = None
    
    async def _get_base_url(self) -> str:
        """
        Get the base URL for the ASR service.
        
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
        Make a request to the ASR service.
        
        Args:
            method: HTTP method
            path: Request path
            **kwargs: Additional arguments for the request
            
        Returns:
            Response: HTTP response
            
        Raises:
            ASRError: If the request fails
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
                    service="asr",
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
                    service="asr",
                    operation=path
                ).observe(latency)
                
                # Check response
                if response.status_code >= 400:
                    # Increment error counter
                    SERVICE_ERRORS.labels(
                        service="asr",
                        operation=path,
                        error_type=f"http_{response.status_code}"
                    ).inc()
                    
                    # Log error
                    logger.error(
                        "ASR service request failed",
                        status_code=response.status_code,
                        response=response.text,
                        url=url
                    )
                    
                    # Raise error
                    raise ASRError(
                        f"ASR service request failed with status code {response.status_code}: {response.text}",
                        response.status_code,
                        {"response": response.text}
                    )
                
                # Return response
                return response
            
            except httpx.TimeoutException as e:
                # Increment error counter
                SERVICE_ERRORS.labels(
                    service="asr",
                    operation=path,
                    error_type="timeout"
                ).inc()
                
                # Log error
                logger.warning(
                    "ASR service request timed out",
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
                        "Retrying ASR service request",
                        retry_count=retry_count,
                        backoff_time=backoff_time,
                        url=url
                    )
                    
                    # Wait before retrying
                    await asyncio.sleep(backoff_time)
                    
                    # Continue to next retry
                    continue
                
                # If we've exhausted retries, raise error
                raise ASRError(
                    f"ASR service request timed out after {retry_count} retries: {str(e)}",
                    None,
                    {"error": str(e)}
                )
            
            except Exception as e:
                # Increment error counter
                SERVICE_ERRORS.labels(
                    service="asr",
                    operation=path,
                    error_type=type(e).__name__
                ).inc()
                
                # Log error
                logger.error(
                    "ASR service request failed",
                    error=str(e),
                    url=url,
                    exc_info=True
                )
                
                # Raise error
                raise ASRError(
                    f"ASR service request failed: {str(e)}",
                    None,
                    {"error": str(e)}
                )
    
    async def transcribe(
        self, 
        audio_data: bytes, 
        language: str,
        audio_format: str = "wav"
    ) -> str:
        """
        Transcribe audio to text.
        
        Args:
            audio_data: Audio data
            language: Language code
            audio_format: Audio format
            
        Returns:
            str: Transcribed text
            
        Raises:
            ASRError: If transcription fails
        """
        try:
            # Prepare request
            files = {
                "file": ("audio." + audio_format, audio_data)
            }
            
            # Include options for language in a format the ASR service expects
            data = {
                "options.language": language
            }
            
            # Make request
            response = await self._make_request(
                method="POST",
                path="/transcribe",
                files=files,
                data=data
            )
            
            # Parse response
            result = response.json()
            
            # Extract transcription
            transcription = result.get("text", "")
            
            # Log success
            logger.info(
                "Audio transcribed successfully",
                language=language,
                audio_format=audio_format,
                transcription_length=len(transcription)
            )
            
            return transcription
        
        except ASRError:
            # Re-raise ASR errors
            raise
        
        except Exception as e:
            # Log error
            logger.error(
                "Transcription failed",
                error=str(e),
                language=language,
                audio_format=audio_format,
                exc_info=True
            )
            
            # Raise error
            raise ASRError(
                f"Transcription failed: {str(e)}",
                None,
                {
                    "error": str(e),
                    "language": language,
                    "audio_format": audio_format
                }
            )
    
    async def check_health(self) -> bool:
        """
        Check if the ASR service is healthy.
        
        Returns:
            bool: True if the service is healthy, False otherwise
        """
        return await self.service_discovery.check_service_health(self.service_config)
