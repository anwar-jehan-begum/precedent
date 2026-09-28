from agent.precedent_ranker import rank_precedents


current_alert = {
    "alert_id": "AML-1068",
    "customer_id": "CUST-019",
    "amount": 840000,
    "typology": "rapid_movement",
    "transaction_pattern": "multiple_transfers"
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


results = rank_precedents(
    current_alert,
    precedents
)


print("\nRanked precedents:\n")

for result in results:
    print(result)