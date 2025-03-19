import logging
import sys
import time
from typing import Any, Dict, Optional

import structlog
from structlog.types import Processor


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Set log level
    log_level_int = getattr(logging, log_level.upper())
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        level=log_level_int,
        stream=sys.stdout,
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """
    Get a structured logger.
    
    Args:
        name: Logger name. If None, will use the module name.
        
    Returns:
        structlog.BoundLogger: Structured logger
    """
    if name is None:
        name = "neural-babel"
    
    return structlog.get_logger(name)


class RequestIdMiddleware:
    """
    Middleware to add request ID to the logging context.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        # Generate request ID
        request_id = f"req-{int(time.time() * 1000)}-{id(scope)}"
        
        # Add request ID to logging context
        logger = get_logger().bind(request_id=request_id)
        
        # Log request
        logger.info(
            "Request started",
            path=scope.get("path", ""),
            method=scope.get("method", ""),
        )
        
        # Process request
        start_time = time.time()
        try:
            return await self.app(scope, receive, send)
        finally:
            # Log response
            duration = time.time() - start_time
            logger.info(
                "Request completed",
                duration=duration,
            )
