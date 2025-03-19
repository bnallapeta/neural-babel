import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import start_http_server

from src.api.endpoints import router
from src.config import get_settings
from src.logging_setup import configure_logging, RequestIdMiddleware, get_logger
from src.utils.errors import NeuralBabelError

# Get settings
settings = get_settings()

# Configure logging
configure_logging(settings.log_level)

# Get logger
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="NeuralBabel",
    description="Speech-to-Speech Translation Pipeline Orchestrator",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request ID middleware
app.add_middleware(RequestIdMiddleware)

# Include router
app.include_router(router)


# Exception handler for NeuralBabelError
@app.exception_handler(NeuralBabelError)
async def neural_babel_error_handler(request: Request, exc: NeuralBabelError):
    """
    Handle NeuralBabelError exceptions.
    """
    logger.error(
        "NeuralBabelError",
        error=str(exc),
        details=exc.details,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "details": exc.details
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Startup event handler.
    """
    logger.info("Starting NeuralBabel service")
    
    # Log configuration
    logger.info(
        "Configuration",
        asr_service=settings.asr_service_name,
        asr_namespace=settings.asr_service_namespace,
        translation_service=settings.translation_service_name,
        translation_namespace=settings.translation_service_namespace,
        tts_service=settings.tts_service_name,
        tts_namespace=settings.tts_service_namespace,
        default_source_lang=settings.default_source_lang,
        default_target_lang=settings.default_target_lang,
        log_level=settings.log_level
    )


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler.
    """
    logger.info("Shutting down NeuralBabel service")


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {
        "service": "NeuralBabel",
        "description": "Speech-to-Speech Translation Pipeline Orchestrator",
        "version": "0.1.0"
    }


# Run the application
if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or default
    port = int(os.environ.get("PORT", 8005))
    
    # Run the application
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
