import pytest
from memory.customer_memory import get_customer_history

def test_customer_memory():
    # Fetch history for Meridian Imports
    result = get_customer_history("Meridian Imports")
    assert result["customer_id"] == "Meridian Imports"
    assert "historical_alerts" in result
    assert "historical_decisions" in result
    assert "observations" in result
    assert "unresolved_issues" in result
