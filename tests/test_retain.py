import pytest
from memory.retain import retain_alert, retain_analyst_decision
from memory.memory_schema import HistoricalCase

def test_retain_alert():
    alert = HistoricalCase(
        alert_id="AML-TEST-001",
        customer_id="Meridian Imports",
        typology="Rapid Movement",
        amount=1000.0,
        transaction_pattern="recurring payroll pattern",
        risk_indicators=[],
        timestamp="2026-09-28T00:00:00Z",
        analyst="A. Kumar",
        agent_recommendation="CLEAR",
        final_decision="CLEAR",
        override=False,
        analyst_reason="Matched customer's recurring payroll pattern"
    )
    result = retain_alert(alert)
    assert result["success"] is True, f"Failed to retain alert: {result}"
