import pytest
from memory.typology_memory import create_typology_model, get_typology_model

def test_mental_models():
    # Attempt to create and wait for the operation to succeed
    create_res = create_typology_model("Test Typology Wait", wait=True)
    assert create_res["success"] is True, f"Failed to create mental model: {create_res.get('error')}"
    
    get_res = get_typology_model("Test Typology Wait")
    assert get_res["success"] is True, "Failed to retrieve mental model after successful creation"
