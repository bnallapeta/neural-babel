import os
from typing import Dict, Any, Optional

from src.config import ServiceConfig
from src.logging_setup import get_logger

logger = get_logger(__name__)


class ServiceDiscovery:
    """
    Service discovery for Kubernetes services.
    """
    
    def __init__(self):
        """
        Initialize the service discovery.
        """
        self.service_urls = {}
        self.service_health = {}
        
        # Check for local endpoints in environment variables
        self.local_endpoints = {
            "asr": os.environ.get("ASR_SERVICE_ENDPOINT"),
            "translation": os.environ.get("TRANSLATION_SERVICE_ENDPOINT"),
            "tts": os.environ.get("TTS_SERVICE_ENDPOINT")
        }
        
        # Log local endpoints if available
        for service_type, endpoint in self.local_endpoints.items():
            if endpoint:
                logger.info(
                    f"Using local endpoint for {service_type} service",
                    service_type=service_type,
                    endpoint=endpoint
                )
    
    def get_service_url(self, service_config: ServiceConfig) -> str:
        """
        Get the URL for a service.
        
        Args:
            service_config: Service configuration
            
        Returns:
            str: Service URL
        """
        # Check if we have a local endpoint for this service type
        if self.local_endpoints.get(service_config.service_type):
            return self.local_endpoints[service_config.service_type]
        
        # Check if we have a cached URL
        if service_config.name in self.service_urls:
            return self.service_urls[service_config.name]
        
        # Build Kubernetes service URL
        service_url = f"http://{service_config.name}.{service_config.namespace}.svc.cluster.local"
        
        # Cache the URL
        self.service_urls[service_config.name] = service_url
        
        # Log the URL
        logger.info(
            f"Discovered service URL",
            service=service_config.name,
            url=service_url
        )
        
        return service_url
    
    async def check_service_health(self, service_config: ServiceConfig) -> bool:
        """
        Check if a service is healthy.
        
        Args:
            service_config: Service configuration
            
        Returns:
            bool: True if the service is healthy, False otherwise
        """
        import httpx
        
        # Get service URL
        service_url = self.get_service_url(service_config)
        
        # Build health check URL
        health_url = f"{service_url}/health"
        
        try:
            # Make request
            async with httpx.AsyncClient() as client:
                response = await client.get(health_url, timeout=2.0)
            
            # Check response
            is_healthy = response.status_code == 200
            
            # Cache health status
            self.service_health[service_config.name] = is_healthy
            
            # Log health status
            logger.info(
                f"Service health check",
                service=service_config.name,
                url=health_url,
                status_code=response.status_code,
                is_healthy=is_healthy
            )
            
            return is_healthy
        
        except Exception as e:
            # Log error
            logger.warning(
                f"Service health check failed",
                service=service_config.name,
                url=health_url,
                error=str(e)
            )
            
            # Cache health status
            self.service_health[service_config.name] = False
            
            return False


# Singleton instance
_service_discovery = None


def get_service_discovery() -> ServiceDiscovery:
    """
    Get the service discovery instance.
    
    Returns:
        ServiceDiscovery: Service discovery instance
    """
    global _service_discovery
    if _service_discovery is None:
        _service_discovery = ServiceDiscovery()
    return _service_discovery
