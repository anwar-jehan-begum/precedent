from dataclasses import dataclass, field
from typing import List


@dataclass
class DecisionResult:
    decision: str
    risk_level: str
    confidence: float
    reason: str
    precedents_used: List[str] = field(default_factory=list)
    key_factors: List[str] = field(default_factory=list)
    human_review_required: bool = False

    def to_dict(self):
        return {
            "decision": self.decision,
            "risk_level": self.risk_level,
            "confidence": self.confidence,
            "reason": self.reason,
            "precedents_used": self.precedents_used,
            "key_factors": self.key_factors,
            "human_review_required": self.human_review_required
        }