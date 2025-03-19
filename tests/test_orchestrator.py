import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.config import PipelineConfig, ServiceConfig
from src.orchestrator.pipeline import TranslationPipeline
from src.utils.errors import PipelineError, ASRError, TranslationError, TTSError


@pytest.fixture
def mock_config():
    """Create a mock pipeline configuration."""
    return PipelineConfig(
        asr_service=ServiceConfig(name="mock-asr", service_type="asr"),
        translation_service=ServiceConfig(name="mock-translation", service_type="translation"),
        tts_service=ServiceConfig(name="mock-tts", service_type="tts"),
        default_source_lang="en",
        default_target_lang="fr",
        supported_language_pairs=[("en", "fr"), ("fr", "en")]
    )


@pytest.fixture
def mock_asr_client():
    """Create a mock ASR client."""
    mock = AsyncMock()
    mock.transcribe.return_value = "Hello, world!"
    mock.check_health.return_value = True
    return mock


@pytest.fixture
def mock_translation_client():
    """Create a mock translation client."""
    mock = AsyncMock()
    mock.translate.return_value = "Bonjour, monde!"
    mock.check_health.return_value = True
    return mock


@pytest.fixture
def mock_tts_client():
    """Create a mock TTS client."""
    mock = AsyncMock()
    mock.synthesize.return_value = b"mock_audio_data"
    mock.check_health.return_value = True
    return mock


@pytest.mark.asyncio
@patch("src.orchestrator.pipeline.ASRClient")
@patch("src.orchestrator.pipeline.TranslationClient")
@patch("src.orchestrator.pipeline.TTSClient")
async def test_translate_speech_success(
    mock_tts_client_class,
    mock_translation_client_class,
    mock_asr_client_class,
    mock_config,
    mock_asr_client,
    mock_translation_client,
    mock_tts_client
):
    """Test successful speech translation."""
    # Set up mocks
    mock_asr_client_class.return_value = mock_asr_client
    mock_translation_client_class.return_value = mock_translation_client
    mock_tts_client_class.return_value = mock_tts_client
    
    # Create pipeline
    pipeline = TranslationPipeline(mock_config)
    
    # Test translation
    result = await pipeline.translate_speech(
        audio_data=b"mock_audio_data",
        source_lang="en",
        target_lang="fr",
        audio_format="wav",
        voice="default"
    )
    
    # Check results
    assert result == b"mock_audio_data"
    
    # Check calls
    mock_asr_client.transcribe.assert_called_once_with(
        audio_data=b"mock_audio_data",
        language="en",
        audio_format="wav"
    )
    
    mock_translation_client.translate.assert_called_once_with(
        text="Hello, world!",
        source_lang="en",
        target_lang="fr"
    )
    
    mock_tts_client.synthesize.assert_called_once_with(
        text="Bonjour, monde!",
        language="fr",
        voice="default",
        audio_format="wav"
    )


@pytest.mark.asyncio
@patch("src.orchestrator.pipeline.ASRClient")
@patch("src.orchestrator.pipeline.TranslationClient")
@patch("src.orchestrator.pipeline.TTSClient")
async def test_translate_speech_asr_error(
    mock_tts_client_class,
    mock_translation_client_class,
    mock_asr_client_class,
    mock_config
):
    """Test ASR error handling."""
    # Set up mocks
    mock_asr_client = AsyncMock()
    mock_asr_client.transcribe.side_effect = ASRError("ASR failed")
    
    mock_translation_client = AsyncMock()
    mock_tts_client = AsyncMock()
    
    mock_asr_client_class.return_value = mock_asr_client
    mock_translation_client_class.return_value = mock_translation_client
    mock_tts_client_class.return_value = mock_tts_client
    
    # Create pipeline
    pipeline = TranslationPipeline(mock_config)
    
    # Test translation with error
    with pytest.raises(PipelineError) as excinfo:
        await pipeline.translate_speech(
            audio_data=b"mock_audio_data",
            source_lang="en",
            target_lang="fr"
        )
    
    # Check error
    assert "ASR failed" in str(excinfo.value)
    assert excinfo.value.stage == "asr"
    
    # Check calls
    mock_asr_client.transcribe.assert_called_once()
    mock_translation_client.translate.assert_not_called()
    mock_tts_client.synthesize.assert_not_called()


@pytest.mark.asyncio
@patch("src.orchestrator.pipeline.ASRClient")
@patch("src.orchestrator.pipeline.TranslationClient")
@patch("src.orchestrator.pipeline.TTSClient")
async def test_check_services_health(
    mock_tts_client_class,
    mock_translation_client_class,
    mock_asr_client_class,
    mock_config,
    mock_asr_client,
    mock_translation_client,
    mock_tts_client
):
    """Test service health checking."""
    # Set up mocks
    mock_asr_client_class.return_value = mock_asr_client
    mock_translation_client_class.return_value = mock_translation_client
    mock_tts_client_class.return_value = mock_tts_client
    
    # Create pipeline
    pipeline = TranslationPipeline(mock_config)
    
    # Test health check
    health = await pipeline.check_services_health()
    
    # Check results
    assert health == {
        "asr": True,
        "translation": True,
        "tts": True
    }
    
    # Check calls
    mock_asr_client.check_health.assert_called_once()
    mock_translation_client.check_health.assert_called_once()
    mock_tts_client.check_health.assert_called_once()
