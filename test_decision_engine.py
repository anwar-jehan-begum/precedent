from agent.decision_engine import DecisionEngine


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
    },

    {
        "alert_id": "AML-0831",
        "customer_id": "CUST-055",
        "amount": 100000,
        "typology": "structuring",
        "transaction_pattern": "cash_deposits",
        "analyst_decision": "ESCALATE",
        "reason": "Unusual deposits"
    }
]


engine = DecisionEngine()

result = engine.analyze(
    alert,
    precedents
)


print("\n==============================")
print("PRECEDENT AI DECISION")
print("==============================")

print("Decision:", result.decision)
print("Risk:", result.risk_level)
print("Confidence:", result.confidence)

print("\nReason:")
print(result.reason)

print("\nPrecedents used:")
for precedent in result.precedents_used:
    print("-", precedent)

print("\nKey factors:")
for factor in result.key_factors:
    print("-", factor)

print(
    "\nHuman review required:",
    result.human_review_required
)

print("==============================")