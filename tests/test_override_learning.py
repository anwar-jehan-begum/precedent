import time
import pytest
from memory.retain import retain_alert, retain_analyst_decision
from memory.precedent_memory import get_precedents
from memory.memory_schema import HistoricalCase

def test_override_learning_loop():
    # Step 1: Create historical alert A
    alert_A = HistoricalCase(
        alert_id="AML-TEST-1042",
        customer_id="Test Customer Override",
        typology="Rapid Movement Test",
        amount=50000.0,
        transaction_pattern="Test override behavioral change pattern",
        risk_indicators=["Velocity"],
        timestamp="2026-09-01T00:00:00Z",
        analyst="Test Analyst",
        agent_recommendation="CLEAR",
        final_decision="ESCALATE",
        override=True,
        analyst_reason="Recent behavioral change."
    )
    retain_alert(alert_A)
    
    # Step 2: Record decision
    retain_analyst_decision(
        alert=alert_A.model_dump(),
        agent_recommendation="CLEAR",
        final_decision="ESCALATE",
        analyst_reason="Recent behavioral change."
    )
    
    # Allow some time for index/observation consolidation if async
    time.sleep(2)
    
    # Step 3: Create similar alert B
    alert_B = {
        "alert_id": "AML-TEST-1068",
        "customer_id": "Test Customer Override",
        "typology": "Rapid Movement Test",
        "transaction_pattern": "Test override behavioral change pattern"
    }
    
    # Step 4: Recall precedents for B
    precedents_result = get_precedents(alert_B)
    assert precedents_result["success"] is not False
    precedents = precedents_result["precedents"]
    
    # Step 5 & 6: Assert that A is retrievable and preserves final decision/override
    found_A = False
    for p in precedents:
        if p["alert_id"] == "AML-TEST-1042":
            found_A = True
            assert p["decision"] == "ESCALATE", "Final human decision not preserved"
            assert p["override"] is True, "Override status not preserved"
            assert "Recent behavioral change" in p["reason"], "Analyst reason not preserved"
            assert p["timestamp"] != "UNKNOWN", "Timestamp was not preserved"
            break
            
    assert found_A, "Did not retrieve the previous override precedent."
