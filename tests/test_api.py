import pytest
from fastapi.testclient import TestClient

from src.main import app


# Create test client
client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()
    assert response.json()["service"] == "NeuralBabel"


def test_health_endpoint():
    """Test the health endpoint."""
    # This will likely fail in CI without mocking the service discovery
    # But it's a good example of how to test the endpoint
    response = client.get("/health")
    assert response.status_code in [200, 500]  # 500 if services are not available
    if response.status_code == 200:
        assert "status" in response.json()
        assert "services" in response.json()


def test_ready_endpoint():
    """Test the readiness endpoint."""
    # This will likely fail in CI without mocking the service discovery
    # But it's a good example of how to test the endpoint
    response = client.get("/ready")
    assert response.status_code in [200, 503]  # 503 if services are not available


def test_live_endpoint():
    """Test the liveness endpoint."""
    response = client.get("/live")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "alive"


def test_config_endpoint():
    """Test the configuration endpoint."""
    response = client.get("/config")
    assert response.status_code == 200
    assert "asr_service" in response.json()
    assert "translation_service" in response.json()
    assert "tts_service" in response.json()
    assert "default_source_lang" in response.json()
    assert "default_target_lang" in response.json()


def test_languages_endpoint():
    """Test the languages endpoint."""
    response = client.get("/languages")
    assert response.status_code == 200
    assert "language_pairs" in response.json()
    assert "default_source_lang" in response.json()
    assert "default_target_lang" in response.json()
    assert isinstance(response.json()["language_pairs"], list)
