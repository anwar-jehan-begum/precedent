from typing import Dict, Any, List
from memory.hindsight_client import get_hindsight_client
from memory.config import config
from memory.customer_memory import get_customer_history

def get_customer_observations(customer_id: str) -> List[str]:
    """Retrieve summarized observations for a customer."""
    history = get_customer_history(customer_id)
    return history.get("observations", [])

def get_typology_observations(typology: str) -> List[str]:
    """Retrieve summarized observations for a typology."""
    from memory.reflect import reflect_on_typology
    result = reflect_on_typology(typology, "What recurring patterns and observations exist?")
    if result["success"]:
        return [result.get("response_text", "")]
    return []

def get_memory_stats() -> Dict[str, Any]:
    """Return memory statistics."""
    client = get_hindsight_client()
    try:
        bank_config = client.get_bank_config(config.HINDSIGHT_BANK_ID)
        memories_res = client.list_memories(bank_id=config.HINDSIGHT_BANK_ID, limit=1)
        total_memories = getattr(memories_res, "total", 0)
        
        return {
            "success": True,
            "total_memories": total_memories,
            "status": "Online",
            "bank_config": bank_config
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
