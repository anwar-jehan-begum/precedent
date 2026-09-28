import time
from typing import Dict, Any, Optional
from memory.hindsight_client import get_hindsight_client
from memory.config import config

def execute_reflect(
    query: str,
    context: Optional[str] = None,
    tags: Optional[list[str]] = None,
    tags_match: str = "any",
    include_facts: bool = True
) -> Dict[str, Any]:
    """Execute a reflect query against Hindsight."""
    client = get_hindsight_client()
    start_time = time.time()
    
    try:
        response = client.reflect(
            bank_id=config.HINDSIGHT_BANK_ID,
            query=query,
            context=context,
            tags=tags,
            tags_match=tags_match,
            include_facts=include_facts
        )
        latency_ms = int((time.time() - start_time) * 1000)
        
        return {
            "success": True,
            "query": query,
            "response_text": getattr(response, "text", ""),
            "latency_ms": latency_ms,
            "response_obj": response
        }
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "query": query,
            "error": str(e),
            "latency_ms": latency_ms
        }

def reflect_on_customer(customer_id: str, query: str) -> Dict[str, Any]:
    """Reflect on accumulated history for a customer."""
    full_query = f"What does the accumulated history tell us about customer {customer_id}? {query}"
    tags = [f"customer:{customer_id}"]
    return execute_reflect(query=full_query, tags=tags, tags_match="all")

def reflect_on_typology(typology: str, query: str) -> Dict[str, Any]:
    """Reflect on accumulated history for a typology."""
    full_query = f"What historical patterns and decisions have accumulated for typology {typology}? {query}"
    tags = [f"typology:{typology.replace(' ', '_')}"]
    return execute_reflect(query=full_query, tags=tags, tags_match="all")
