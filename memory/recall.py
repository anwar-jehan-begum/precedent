import time
from typing import Dict, Any, List, Optional
from memory.hindsight_client import get_hindsight_client
from memory.config import config

def execute_recall(
    query: str, 
    tags: Optional[List[str]] = None,
    tags_match: str = "any",
    temporal_window: Optional[Dict[str, Any]] = None,
    trace: bool = True
) -> Dict[str, Any]:
    """Execute a raw recall query against Hindsight."""
    client = get_hindsight_client()
    start_time = time.time()
    
    try:
        response = client.recall(
            bank_id=config.HINDSIGHT_BANK_ID,
            query=query,
            tags=tags,
            tags_match=tags_match,
            temporal_window=temporal_window,
            trace=trace
        )
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Format response
        result_count = len(response.results) if hasattr(response, 'results') else 0
        return {
            "success": True,
            "query": query,
            "result_count": result_count,
            "latency_ms": latency_ms,
            "results": response.results if hasattr(response, 'results') else [],
            "trace_available": trace,
            "response_obj": response
        }
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "query": query,
            "error": str(e),
            "latency_ms": latency_ms,
            "result_count": 0,
            "results": []
        }
