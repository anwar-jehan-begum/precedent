import json
import time
from typing import Dict, Any, Optional
from memory.hindsight_client import get_hindsight_client
from memory.config import config
from memory.memory_schema import HistoricalCase, DecisionMemory

def retain_alert(alert: HistoricalCase) -> Dict[str, Any]:
    """Retains a new alert into memory."""
    client = get_hindsight_client()
    
    # Construct a comprehensive fact sentence
    content = f"Alert {alert.alert_id} for customer {alert.customer_id} ({alert.typology}). "
    content += f"Amount: {alert.amount} {alert.currency}. "
    content += f"Transaction pattern: {alert.transaction_pattern}. "
    if alert.risk_indicators:
        content += f"Risk indicators: {', '.join(alert.risk_indicators)}. "
    
    if alert.agent_recommendation:
        content += f"Agent recommended {alert.agent_recommendation}. "
    if alert.final_decision:
        content += f"Human analyst {alert.analyst} decided {alert.final_decision}. "
        if alert.override:
            content += "This was an OVERRIDE of the agent recommendation. "
        if alert.analyst_reason:
            content += f"Reason: '{alert.analyst_reason}'. "
    
    if alert.outcome:
        content += f"Outcome: {alert.outcome}. "

    tags = [
        f"customer:{alert.customer_id}",
        f"alert:{alert.alert_id}",
        f"typology:{alert.typology.replace(' ', '_')}"
    ]
    
    metadata = {
        "alert_id": alert.alert_id,
        "customer_id": alert.customer_id,
        "typology": alert.typology,
        "record_type": "alert",
        "agent_recommendation": alert.agent_recommendation or "",
        "final_decision": alert.final_decision or "",
        "override": str(alert.override),
        "analyst_reason": alert.analyst_reason or "",
        "timestamp": alert.timestamp or ""
    }
    
    start_time = time.time()
    response = client.retain(
        bank_id=config.HINDSIGHT_BANK_ID,
        content=content,
        context="Historical Alert Details",
        tags=tags,
        metadata=metadata
    )
    
    latency_ms = int((time.time() - start_time) * 1000)
    return {
        "success": True,
        "content": content,
        "response": response,
        "latency_ms": latency_ms
    }

def retain_analyst_decision(
    alert: Dict[str, Any],
    agent_recommendation: str,
    final_decision: str,
    analyst_reason: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Retains the final human analyst decision for an alert."""
    client = get_hindsight_client()
    
    alert_id = alert.get("alert_id")
    customer_id = alert.get("customer_id")
    typology = alert.get("typology", "unknown")
    
    override = (agent_recommendation != final_decision)
    
    content = f"For alert {alert_id} (customer {customer_id}), the agent recommended {agent_recommendation}. "
    content += f"The human analyst reviewed it and made a final decision to {final_decision}. "
    if override:
        content += "This was an OVERRIDE. "
    content += f"Analyst reason: '{analyst_reason}'."
    
    tags = [
        f"customer:{customer_id}",
        f"alert:{alert_id}",
        "decision",
        f"typology:{typology.replace(' ', '_')}"
    ]
    if override:
        tags.append("override")
        
    merged_metadata = {
        "alert_id": str(alert_id),
        "customer_id": str(customer_id),
        "typology": str(typology),
        "record_type": "decision",
        "agent_recommendation": str(agent_recommendation),
        "final_decision": str(final_decision),
        "override": str(override),
        "analyst_reason": str(analyst_reason),
        "timestamp": str(alert.get("timestamp", ""))
    }
    if metadata:
        for k, v in metadata.items():
            merged_metadata[k] = str(v)
            
    start_time = time.time()
    response = client.retain(
        bank_id=config.HINDSIGHT_BANK_ID,
        content=content,
        context="Analyst Decision Record",
        tags=tags,
        metadata=merged_metadata
    )
    
    latency_ms = int((time.time() - start_time) * 1000)
    return {
        "success": True,
        "content": content,
        "latency_ms": latency_ms,
        "response": response
    }
