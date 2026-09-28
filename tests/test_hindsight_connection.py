import pytest
from memory.health import check_hindsight_configuration

def test_hindsight_connection():
    health = check_hindsight_configuration()
    assert health["ok"] is True, f"Connection failed: {health.get('message')}"
    assert "precedent-aml" in health["bank_id"]
