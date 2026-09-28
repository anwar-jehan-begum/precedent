import pytest
from memory.reflect import reflect_on_customer
from memory.evidence import get_memory_evidence

def test_reflect():
    res = reflect_on_customer("Meridian Imports", "Summarize")
    assert res["success"] is True
    assert "response_text" in res
    
    # Extract evidence
    evidence = get_memory_evidence(res)
    assert isinstance(evidence, list)
