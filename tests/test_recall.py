import pytest
from memory.recall import execute_recall

def test_recall_basic():
    query = "What decision was made for Meridian Imports in AML-TEST-001?"
    result = execute_recall(query=query)
    assert result["success"] is True, f"Failed to execute recall: {result}"
    # Verify relevant memory comes back
    assert result["result_count"] > 0, "No results returned for recall"
