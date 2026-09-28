from typing import Dict, Any, List

def extract_evidence(response_obj: Any) -> List[Dict[str, Any]]:
    """Extract evidence from a Hindsight response (Recall or Reflect)."""
    evidence_items = []
    
    # Check if this is a Reflect response with facts
    if hasattr(response_obj, "facts") and response_obj.facts:
        for fact in response_obj.facts:
            # Fact might be a ReflectFact object
            item = {
                "source_text": getattr(fact, "text", str(fact)),
                "memory_id": getattr(fact, "id", None),
                "source_type": "ReflectFact"
            }
            evidence_items.append(item)
            
    # Check if this is a Recall response with results
    elif hasattr(response_obj, "results") and response_obj.results:
        for result in response_obj.results:
            item = {
                "source_text": getattr(result, "text", str(result)),
                "memory_id": getattr(result, "id", None),
                "source_type": "RecallResult",
                "document_id": getattr(result, "document_id", None),
                "chunk_id": getattr(result, "chunk_id", None),
                "source_fact_ids": getattr(result, "source_fact_ids", []),
                "metadata": getattr(result, "metadata", {})
            }
            evidence_items.append(item)
            
    return evidence_items

def get_memory_evidence(response_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Public wrapper to get evidence items from a dictionary containing the original response obj."""
    if "response_obj" in response_dict:
        return extract_evidence(response_dict["response_obj"])
    return []
