from agent.schemas import DecisionResult


result = DecisionResult(
    decision="ESCALATE",
    risk_level="HIGH",
    confidence=0.87,
    reason="Similar historical cases were escalated.",
    precedents_used=["AML-1042", "AML-0987"],
    key_factors=["rapid movement", "new counterparty"],
    human_review_required=True
)

print(result.to_dict())