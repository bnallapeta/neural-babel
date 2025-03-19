import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.config import ServiceConfig
from src.clients.asr_client import ASRClient
from src.clients.translation_client import TranslationClient
from src.clients.tts_client import TTSClient
from src.utils.errors import ASRError, TranslationError, TTSError


@pytest.fixture
def mock_service_discovery():
    """Create a mock service discovery."""
    mock = AsyncMock()
    mock.get_service_url.return_value = "http://mock-service:8000"
    mock.check_service_health.return_value = True
    return mock


@pytest.fixture
def mock_response():
    """Create a mock HTTP response."""
    mock = MagicMock()
    mock.status_code = 200
    mock.text = "Success"
    return mock


@pytest.fixture
def mock_asr_config():
    """Create a mock ASR service configuration."""
    return ServiceConfig(
        name="mock-asr",
        namespace="default",
        service_type="asr",
        timeout=1.0,
        retries=1
    )


@pytest.fixture
def mock_translation_config():
    """Create a mock translation service configuration."""
    return ServiceConfig(
        name="mock-translation",
        namespace="default",
        service_type="translation",
        timeout=1.0,
        retries=1
    )


@pytest.fixture
def mock_tts_config():
    """Create a mock TTS service configuration."""
    return ServiceConfig(
        name="mock-tts",
        namespace="default",
        service_type="tts",
        timeout=1.0,
        retries=1
    )


@pytest.mark.asyncio
@patch("src.clients.asr_client.get_service_discovery")
@patch("httpx.AsyncClient.request")
async def test_asr_client_transcribe(
    mock_request,
    mock_get_service_discovery,
    mock_service_discovery,
    mock_response,
    mock_asr_config
):
    """Test ASR client transcription."""
    # Set up mocks
    mock_get_service_discovery.return_value = mock_service_discovery
    mock_response.json.return_value = {"text": "Hello, world!"}
    mock_request.return_value = mock_response
    
    # Create client
    client = ASRClient(mock_asr_config)
    
    # Test transcription
    result = await client.transcribe(
        audio_data=b"mock_audio_data",
        language="en",
        audio_format="wav"
    )
    
    # Check results
    assert result == "Hello, world!"
    
    # Check calls
    mock_service_discovery.get_service_url.assert_called_once_with(mock_asr_config)
    mock_request.assert_called_once()


@pytest.mark.asyncio
@patch("src.clients.translation_client.get_service_discovery")
@patch("httpx.AsyncClient.request")
async def test_translation_client_translate(
    mock_request,
    mock_get_service_discovery,
    mock_service_discovery,
    mock_response,
    mock_translation_config
):
    """Test translation client translation."""
    # Set up mocks
    mock_get_service_discovery.return_value = mock_service_discovery
    mock_response.json.return_value = {"translation": "Bonjour, monde!"}
    mock_request.return_value = mock_response
    
    # Create client
    client = TranslationClient(mock_translation_config)
    
    # Test translation
    result = await client.translate(
        text="Hello, world!",
        source_lang="en",
        target_lang="fr"
    )
    
    # Check results
    assert result == "Bonjour, monde!"
    
    # Check calls
    mock_service_discovery.get_service_url.assert_called_once_with(mock_translation_config)
    mock_request.assert_called_once()


@pytest.mark.asyncio
@patch("src.clients.tts_client.get_service_discovery")
@patch("httpx.AsyncClient.request")
async def test_tts_client_synthesize(
    mock_request,
    mock_get_service_discovery,
    mock_service_discovery,
    mock_response,
    mock_tts_config
):
    """Test TTS client synthesis."""
    # Set up mocks
    mock_get_service_discovery.return_value = mock_service_discovery
    mock_response.content = b"mock_audio_data"
    mock_request.return_value = mock_response
    
    # Create client
    client = TTSClient(mock_tts_config)
    
    # Test synthesis
    result = await client.synthesize(
        text="Hello, world!",
        language="en",
        voice="default",
        audio_format="wav"
    )
    
    # Check results
    assert result == b"mock_audio_data"
    
    # Check calls
    mock_service_discovery.get_service_url.assert_called_once_with(mock_tts_config)
    mock_request.assert_called_once()


@pytest.mark.asyncio
@patch("src.clients.asr_client.get_service_discovery")
@patch("httpx.AsyncClient.request")
async def test_asr_client_error(
    mock_request,
    mock_get_service_discovery,
    mock_service_discovery,
    mock_asr_config
):
    """Test ASR client error handling."""
    # Set up mocks
    mock_get_service_discovery.return_value = mock_service_discovery
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_request.return_value = mock_response
    
    # Create client
    client = ASRClient(mock_asr_config)
    
    # Test transcription with error
    with pytest.raises(ASRError) as excinfo:
        await client.transcribe(
            audio_data=b"mock_audio_data",
            language="en",
            audio_format="wav"
        )
    
    # Check error
    assert "500" in str(excinfo.value)
    assert "Internal Server Error" in str(excinfo.value)
