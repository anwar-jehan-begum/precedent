from agent.prompts import build_aml_prompt


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
        "similarity": 0.99,
        "decision": "CLEAR",
        "reason": "Recurring payroll pattern"
    },
    {
        "alert_id": "AML-0987",
        "similarity": 0.98,
        "decision": "ESCALATE",
        "reason": "New counterparties"
    }
]


prompt = build_aml_prompt(
    alert,
    precedents
)


print(prompt)