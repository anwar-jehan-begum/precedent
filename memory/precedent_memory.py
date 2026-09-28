import json
from typing import Dict, Any, List
from memory.recall import execute_recall
from memory.memory_schema import Precedent

def get_precedents(alert: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve historical precedents for a given alert."""
    customer_id = alert.get("customer_id")
    typology = alert.get("typology", "")
    transaction_pattern = alert.get("transaction_pattern", "")
    
    # Construct a query to find similar precedents
    query = f"Previous alerts and decisions for customer {customer_id} involving typology '{typology}' and pattern '{transaction_pattern}'."
    
    # We want to search broadly but prioritize this customer and typology
    tags = [f"customer:{customer_id}", f"typology:{typology.replace(' ', '_')}", "decision"]
    
    # Execute the recall
    recall_result = execute_recall(query=query, tags=tags, tags_match="any")
    
    precedents: List[Dict[str, Any]] = []
    
    if recall_result["success"] and recall_result["results"]:
        for res in recall_result["results"]:
            text = res.text if hasattr(res, "text") else str(res)
            
            metadata = getattr(res, "metadata", {}) or {}
            
            # Use metadata if available, else fallback to text heuristics
            if metadata and "final_decision" in metadata:
                decision = metadata.get("final_decision", "UNKNOWN")
                is_override = metadata.get("override", "False").lower() == "true"
                extracted_alert_id = metadata.get("alert_id", "UNKNOWN")
                reason = metadata.get("analyst_reason", text)
                timestamp = metadata.get("timestamp", getattr(res, "timestamp", "UNKNOWN"))
            else:
                decision = "UNKNOWN"
                is_override = False
                extracted_alert_id = "UNKNOWN"
                reason = "No authoritative metadata available."
                timestamp = getattr(res, "timestamp", "UNKNOWN")

            
            precedent = {
                "alert_id": extracted_alert_id.upper(),
                "decision": decision,
                "reason": reason,
                "typology": typology,
                "timestamp": timestamp if timestamp else "UNKNOWN",
                "memory_id": getattr(res, "id", "UNKNOWN"),
                "source": text,
                "relevance_reason": "Same customer and highly similar transaction pattern" if customer_id in text else "Similar transaction pattern",
                "override": is_override,
                "has_metadata": bool(metadata)
            }
            precedents.append(precedent)

    # Deduplicate by alert_id, prioritizing ones with metadata
    deduped_precedents = {}
    for p in precedents:
        aid = p["alert_id"]
        if aid == "UNKNOWN":
            deduped_precedents[p["memory_id"]] = p
        elif aid not in deduped_precedents or (p["has_metadata"] and not deduped_precedents[aid]["has_metadata"]):
            deduped_precedents[aid] = p
            
    final_precedents = list(deduped_precedents.values())

    if not recall_result.get("success", False):
        return {
            "success": False,
            "error": recall_result.get("error", "Unknown error during recall"),
            "alert_id": alert.get("alert_id"),
            "customer_id": customer_id,
            "precedents": [],
            "count": 0,
            "query": query,
            "evidence_available": False,
            "latency_ms": recall_result.get("latency_ms", 0),
        }

    return {
        "success": True,
        "alert_id": alert.get("alert_id"),
        "customer_id": customer_id,
        "precedents": final_precedents,
        "count": len(final_precedents),
        "query": query,
        "evidence_available": len(final_precedents) > 0,
        "latency_ms": recall_result.get("latency_ms", 0),
        "trace_available": recall_result.get("trace_available", False)
    }
