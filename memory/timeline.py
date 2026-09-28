from typing import Dict, Any, List
from memory.customer_memory import get_customer_history

def get_customer_timeline(customer_id: str) -> List[Dict[str, Any]]:
    """Return chronological events for a customer's timeline."""
    history = get_customer_history(customer_id)
    
    events = []
    for alert in history.get("historical_alerts", []):
        if alert.get("timestamp"):
            metadata = alert.get("metadata", {})
            events.append({
                "timestamp": alert.get("timestamp"),
                "type": "alert",
                "alert_id": metadata.get("alert_id", "UNKNOWN"),
                "decision": metadata.get("final_decision", "UNKNOWN"),
                "summary": alert.get("text", "")
            })
            
    for decision in history.get("historical_decisions", []):
        if decision.get("timestamp"):
            events.append({
                "timestamp": decision.get("timestamp"),
                "type": "decision",
                "summary": decision.get("text", "")
            })
            
    # Sort chronologically
    events.sort(key=lambda x: x["timestamp"])
    
    return events
