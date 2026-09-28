import time
from typing import Dict, Any, Optional
from memory.hindsight_client import get_hindsight_client
from memory.config import config

def wait_for_operation(operation_id: str, max_wait_sec: int = 30) -> bool:
    """Wait for an asynchronous operation to complete."""
    if not operation_id:
        return True
    
    client = get_hindsight_client()
    start_time = time.time()
    
    import asyncio
    
    while time.time() - start_time < max_wait_sec:
        try:
            status_res = asyncio.run(client.operations.get_operation_status(
                bank_id=config.HINDSIGHT_BANK_ID,
                operation_id=operation_id
            ))
            status = getattr(status_res, "status", "").lower()
            if status in ["completed", "success", "done"]:
                return True
            if status in ["failed", "error", "cancelled"]:
                return False
        except Exception:
            pass
        time.sleep(2)
        
    return False

def create_typology_model(typology: str, wait: bool = True) -> Dict[str, Any]:
    """Create a new mental model for a typology."""
    client = get_hindsight_client()
    model_id = f"typology-{typology.lower().replace(' ', '-')}"
    query = f"What historical patterns, analyst decisions, exceptions, recurring observations, and unresolved concerns have accumulated for {typology}?"
    
    start_time = time.time()
    try:
        response = client.create_mental_model(
            bank_id=config.HINDSIGHT_BANK_ID,
            id=model_id,
            name=f"{typology} Intelligence",
            source_query=query,
            tags=[f"typology:{typology.replace(' ', '_')}"]
        )
        
        op_id = getattr(response, "operation_id", None)
        if wait and op_id:
            if not wait_for_operation(op_id):
                latency_ms = int((time.time() - start_time) * 1000)
                return {
                    "success": False,
                    "model_id": model_id,
                    "error": f"Operation {op_id} timed out or failed.",
                    "latency_ms": latency_ms
                }
            
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "success": True,
            "model_id": model_id,
            "operation_id": op_id,
            "latency_ms": latency_ms
        }
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        # If it already exists, treat it as a success for creation
        if "409" in str(e) or "already exists" in str(e).lower():
            return {
                "success": True,
                "model_id": model_id,
                "message": "Model already existed",
                "latency_ms": latency_ms
            }
        return {
            "success": False,
            "model_id": model_id,
            "error": str(e),
            "latency_ms": latency_ms
        }

def refresh_typology_model(typology: str, wait: bool = True) -> Dict[str, Any]:
    """Trigger a refresh of a typology mental model."""
    client = get_hindsight_client()
    model_id = f"typology-{typology.lower().replace(' ', '-')}"
    
    start_time = time.time()
    try:
        response = client.refresh_mental_model(
            bank_id=config.HINDSIGHT_BANK_ID,
            mental_model_id=model_id
        )
        
        op_id = getattr(response, "operation_id", None)
        if wait and op_id:
            if not wait_for_operation(op_id):
                latency_ms = int((time.time() - start_time) * 1000)
                return {
                    "success": False,
                    "model_id": model_id,
                    "error": f"Refresh operation {op_id} timed out or failed.",
                    "latency_ms": latency_ms
                }
            
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "success": True,
            "model_id": model_id,
            "operation_id": op_id,
            "latency_ms": latency_ms
        }
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "model_id": model_id,
            "error": str(e),
            "latency_ms": latency_ms
        }

def get_typology_model(typology: str) -> Dict[str, Any]:
    """Get the current state of a typology mental model."""
    client = get_hindsight_client()
    model_id = f"typology-{typology.lower().replace(' ', '-')}"
    
    start_time = time.time()
    try:
        response = client.get_mental_model(
            bank_id=config.HINDSIGHT_BANK_ID,
            mental_model_id=model_id
        )
        latency_ms = int((time.time() - start_time) * 1000)
        
        return {
            "success": True,
            "model_id": model_id,
            "summary": getattr(response, "summary", ""),
            "model": response,
            "latency_ms": latency_ms
        }
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "model_id": model_id,
            "error": str(e),
            "latency_ms": latency_ms
        }

def get_typology_knowledge(typology: str) -> Dict[str, Any]:
    """Retrieve mental model or reflect knowledge for a typology."""
    result = get_typology_model(typology)
    if result["success"] and result.get("summary"):
        return result
        
    # If not available, fallback to a reflect query
    from memory.reflect import reflect_on_typology
    return reflect_on_typology(typology, "Summarize knowledge.")
