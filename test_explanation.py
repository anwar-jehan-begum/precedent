from agent.decision_engine import DecisionEngine
from agent.explanation import format_decision_explanation


alert = {
    "alert_id": "AML-1068",
    "customer_id": "CUST-019",
    "amount": 840000,
    "currency": "INR",
    "typology": "rapid_movement",
    "transaction_pattern": "multiple_transfers",
    "pep_match": False,
    "watchlist_match": False
}


precedents = [
    {
        "alert_id": "AML-1042",
        "customer_id": "CUST-019",
        "amount": 820000,
        "typology": "rapid_movement",
        "transaction_pattern": "multiple_transfers",
        "analyst_decision": "CLEAR",
        "reason": "Recurring payroll pattern"
    },
    {
        "alert_id": "AML-0987",
        "customer_id": "CUST-019",
        "amount": 790000,
        "typology": "rapid_movement",
        "transaction_pattern": "multiple_transfers",
        "analyst_decision": "ESCALATE",
        "reason": "New counterparties"
    }
]


engine = DecisionEngine()

result = engine.analyze(
    alert,
    precedents
)

print("\n" + format_decision_explanation(result))