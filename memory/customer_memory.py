import time
from typing import Dict, Any, List
from memory.recall import execute_recall

def get_customer_history(customer_id: str, include_unresolved: bool = True) -> Dict[str, Any]:
    """Retrieve full history for a given customer."""
    query = f"Provide all historical alerts, analyst decisions, recurring patterns, observations, unresolved issues, and recent events for customer {customer_id}."
    tags = [f"customer:{customer_id}"]
    
    # We require all results to be tagged with the customer ID
    recall_result = execute_recall(query=query, tags=tags, tags_match="all")
    
    historical_alerts = []
    historical_decisions = []
    observations = []
    
    if recall_result["success"] and recall_result["results"]:
        for res in recall_result["results"]:
            text = res.text if hasattr(res, "text") else str(res)
            
            metadata = getattr(res, "metadata", {}) or {}
            
            if "decision" in [t.lower() for t in getattr(res, "tags", [])] or metadata.get("record_type") == "decision":
                historical_decisions.append({
                    "text": text,
                    "memory_id": getattr(res, "id", None),
                    "timestamp": metadata.get("timestamp", getattr(res, "timestamp", None)),
                    "metadata": metadata
                })
            elif "observation" in [t.lower() for t in getattr(res, "tags", [])]:
                observations.append(text)
            elif "alert" in [t.lower() for t in getattr(res, "tags", [])] or metadata.get("record_type") == "alert":
                historical_alerts.append({
                    "text": text,
                    "memory_id": getattr(res, "id", None),
                    "timestamp": metadata.get("timestamp", getattr(res, "timestamp", None)),
                    "metadata": metadata
                })
                
    unresolved_issues = []
    if include_unresolved:
        from memory.reflect import reflect_on_customer
        reflect_result = reflect_on_customer(customer_id, "What are the unresolved issues or ongoing concerns?")
        if reflect_result.get("success") and reflect_result.get("response_text"):
            unresolved_issues.append(reflect_result.get("response_text"))

    # Sort historical alerts by timestamp descending for recent_events
    sorted_alerts = sorted(
        historical_alerts, 
        key=lambda x: x.get("timestamp") or "", 
        reverse=True
    )

    return {
        "customer_id": customer_id,
        "historical_alerts": historical_alerts,
        "historical_decisions": historical_decisions,
        "observations": observations,
        "unresolved_issues": unresolved_issues,
        "recent_events": sorted_alerts[:5]
    }
