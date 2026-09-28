def build_aml_prompt(alert, precedents):
    prompt = f"""
You are an AML transaction-monitoring decision assistant.

Your task is to analyze the current AML alert using ONLY the evidence
provided below.

CURRENT ALERT
-------------
Alert ID: {alert.get("alert_id")}
Customer ID: {alert.get("customer_id")}
Amount: {alert.get("amount")}
Currency: {alert.get("currency", "INR")}
Typology: {alert.get("typology")}
Transaction Pattern: {alert.get("transaction_pattern")}

PEP Match: {alert.get("pep_match", False)}
Watchlist Match: {alert.get("watchlist_match", False)}

HISTORICAL PRECEDENTS
---------------------
"""

    if precedents:
        # FIX 3 — compute the actual decision distribution and surface it
        # explicitly so the model cannot claim unanimity when decisions are mixed.
        clear_count = sum(1 for p in precedents if str(p.get("decision", "")).upper() == "CLEAR")
        escalate_count = sum(1 for p in precedents if str(p.get("decision", "")).upper() == "ESCALATE")
        prompt += f"Decision distribution across retrieved precedents: {escalate_count} ESCALATE, {clear_count} CLEAR\n"

        for precedent in precedents:
            prompt += f"""
Alert ID: {precedent.get("alert_id")}
Similarity: {precedent.get("similarity")}
Previous Decision: {precedent.get("decision")}
Reason: {precedent.get("reason")}
"""
    else:
        prompt += "\nNo relevant historical precedents were found.\n"

    prompt += """
DECISION RULES
--------------
1. Choose exactly one decision:
   CLEAR
   ESCALATE

2. Do not invent facts.

3. Use historical precedents as supporting evidence.

4. If historical precedents show mixed decisions (some CLEAR, some ESCALATE),
   you MUST explicitly acknowledge the conflict in your reason. Do NOT claim
   that precedents were unanimous unless every retrieved precedent agrees.

5. A PEP or watchlist match requires human review.

6. The final explanation must be based only on the supplied evidence.

Return ONLY valid JSON using exactly this structure:

{
    "decision": "CLEAR or ESCALATE",
    "risk_level": "LOW, MEDIUM, or HIGH",
    "confidence": 0.0,
    "reason": "Brief evidence-based explanation",
    "key_factors": [
        "factor 1",
        "factor 2"
    ]
}

Requirements:

- decision must be exactly CLEAR or ESCALATE
- risk_level must be exactly LOW, MEDIUM, or HIGH
- confidence must be a number between 0.0 and 1.0
- reason must explain the decision using supplied evidence
- key_factors must contain the main evidence used
- do not add fields
- do not invent facts
- return JSON only
"""

    return prompt