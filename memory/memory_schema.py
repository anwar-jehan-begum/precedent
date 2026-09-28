from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class HistoricalCase(BaseModel):
    alert_id: str
    customer_id: str
    typology: str
    amount: float
    currency: str = "USD"
    transaction_pattern: str
    risk_indicators: List[str]
    timestamp: str
    analyst: str
    agent_recommendation: str
    final_decision: str
    override: bool
    analyst_reason: str
    outcome: Optional[str] = None
    memory_id: Optional[str] = None
    source: Optional[str] = None

class Precedent(BaseModel):
    alert_id: str
    customer_id: str
    typology: str
    decision: str
    reason: str
    timestamp: str
    outcome: Optional[str] = None
    memory_id: Optional[str] = None
    relevance_reason: Optional[str] = None
    source: Optional[str] = None
    derived_similarity: Optional[float] = None

class EvidenceItem(BaseModel):
    memory_id: Optional[str] = None
    alert_id: Optional[str] = None
    source_text: str
    source_type: str
    relationship: Optional[str] = None
    metadata: Optional[dict] = None

class CustomerHistory(BaseModel):
    customer_id: str
    historical_alerts: List[HistoricalCase] = Field(default_factory=list)
    historical_decisions: List[dict] = Field(default_factory=list)
    observations: List[str] = Field(default_factory=list)
    unresolved_issues: List[str] = Field(default_factory=list)
    recent_events: List[dict] = Field(default_factory=list)

class DecisionMemory(BaseModel):
    alert_id: str
    customer_id: str
    agent_recommendation: str
    final_decision: str
    override: bool
    analyst_reason: str
    timestamp: str
    typology: str
    precedent_ids: List[str] = Field(default_factory=list)
