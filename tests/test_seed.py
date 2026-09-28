import pytest
from memory.seed import seed_data
from memory.customer_memory import get_customer_history

def test_seed():
    res = seed_data()
    assert res["success"] is True

    # Verify that the expected synthetic customer history can actually be recalled
    meridian = get_customer_history("Meridian Imports", include_unresolved=False)
    assert len(meridian["historical_alerts"]) > 0, "Failed to recall Meridian Imports alerts"
    
    nova = get_customer_history("Nova Trading", include_unresolved=False)
    assert len(nova["historical_alerts"]) > 0, "Failed to recall Nova Trading alerts"
    
    acme = get_customer_history("Acme Retail", include_unresolved=False)
    assert len(acme["historical_alerts"]) > 0, "Failed to recall Acme Retail alerts"
