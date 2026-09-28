import time
import pytest
from memory.retain import retain_analyst_decision
from memory.precedent_memory import get_precedents

def test_decision_memory():
    alert = {
        "alert_id": "AML-DECISION-TEST",
        "customer_id": "Decision Test Customer",
        "typology": "Test Typology",
        "transaction_pattern": "Pattern A"
    }
    
    retain_analyst_decision(
        alert=alert,
        agent_recommendation="CLEAR",
        final_decision="ESCALATE",
        analyst_reason="Testing decision retention."
    )
    
    time.sleep(2)
    
    precedents = get_precedents(alert)
    assert precedents["success"] is True
    
    found = False
    for p in precedents["precedents"]:
        if p["alert_id"] == "AML-DECISION-TEST":
            found = True
            assert p["decision"] == "ESCALATE"
            assert p["override"] is True
            assert "Testing decision retention" in p["reason"]
    
    assert found, "Decision memory was not correctly retrieved."
