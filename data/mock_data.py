"""
Mock data layer for PRECEDENT (Member 3 — UI shell).

Every function here is a clean, swappable interface. Later, Member 1
(Hindsight / memory retrieval) and Member 2 (AI reasoning / evaluation)
will replace the bodies of these functions with real implementations
without requiring any changes to the UI layer.

DEMO / MOCK DATA ONLY — no real customer or transaction data.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta

random.seed(7)

# ---------------------------------------------------------------------------
# Static reference data
# ---------------------------------------------------------------------------

TYPOLOGIES = {
    "Rapid Movement": {
        "description": (
            "Funds move through an account in unusually fast succession, often "
            "within hours, with little to no dwell time — a common layering "
            "technique to obscure the origin of funds."
        ),
        "indicators": [
            "High velocity of in/out transfers",
            "Minimal balance retention",
            "New or unverified counterparties",
        ],
        "guardrails": [
            "Check PEP / sanctions watchlist status before escalation",
            "Verify counterparty KYC completeness",
        ],
    },
    "Structuring": {
        "description": (
            "Multiple transactions kept just under reporting thresholds, "
            "spread across a short time window, suggesting deliberate "
            "avoidance of reporting requirements."
        ),
        "indicators": [
            "Repeated deposits below threshold",
            "Short time intervals between deposits",
            "Consistent round-number amounts",
        ],
        "guardrails": [
            "Confirm threshold values for jurisdiction",
            "Cross-check against known structuring precedents",
        ],
    },
    "Payroll": {
        "description": (
            "Recurring, predictable payroll-style disbursements consistent "
            "with legitimate business activity."
        ),
        "indicators": [
            "Fixed periodicity",
            "Consistent recipient list",
            "Amounts consistent with declared business size",
        ],
        "guardrails": [
            "Confirm business registration is current",
        ],
    },
}

PEP_WATCHLIST_STATUS = {
    "Meridian Imports": {"pep": False, "watchlist": False},
    "Nova Trading": {"pep": False, "watchlist": False},
    "Acme Retail": {"pep": False, "watchlist": False},
}


def _days_ago(n: int) -> str:
    return (datetime.now() - timedelta(days=n)).strftime("%d %b %Y")


# ---------------------------------------------------------------------------
# Alerts (current, open queue)
# ---------------------------------------------------------------------------

ALERTS = [
    {
        "id": "AML-1068",
        "customer": "Meridian Imports",
        "customer_id": "CUST-3391",
        "amount": 840000,
        "currency": "INR",
        "typology": "Rapid Movement",
        "risk": "HIGH",
        "signals": [
            "Multiple transfers in a 6-hour window",
            "New counterparties never seen before",
            "Sudden behavioral change vs 12-month baseline",
        ],
        "precedent_count": 3,
        "confidence": 87,
        "status": "OPEN",
        "geography": ["Domestic — Mumbai", "Cross-border — Singapore"],
    },
    {
        "id": "AML-1067",
        "customer": "Nova Trading",
        "customer_id": "CUST-2210",
        "amount": 210000,
        "currency": "INR",
        "typology": "Structuring",
        "risk": "MEDIUM",
        "signals": [
            "Repeated deposits just under reporting threshold",
            "Short intervals between deposits",
        ],
        "precedent_count": 2,
        "confidence": 78,
        "status": "OPEN",
        "geography": ["Domestic — Pune"],
    },
    {
        "id": "AML-1066",
        "customer": "Acme Retail",
        "customer_id": "CUST-1187",
        "amount": 140000,
        "currency": "INR",
        "typology": "Payroll",
        "risk": "LOW",
        "signals": [
            "Recurring payroll pattern",
        ],
        "precedent_count": 5,
        "confidence": 92,
        "status": "OPEN",
        "geography": ["Domestic — Hyderabad"],
    },
]

# ---------------------------------------------------------------------------
# Historical precedent cases (closed, decided)
# ---------------------------------------------------------------------------

PRECEDENTS = {
    "AML-1068": [
        {
            "id": "AML-1042",
            "similarity": 92,
            "decision": "CLEAR",
            "pattern": "Recurring payroll pattern",
            "date": "14 Aug 2026",
            "reason": (
                "Disbursements matched the customer's declared payroll cycle "
                "and recipient list exactly; no new counterparties involved."
            ),
            "analyst": "R. Sharma",
            "matching_factors": ["Customer segment", "Transaction frequency"],
            "differing_factors": ["No new counterparties (unlike current alert)"],
        },
        {
            "id": "AML-0987",
            "similarity": 89,
            "decision": "ESCALATE",
            "pattern": "New counterparty pattern",
            "date": "02 Aug 2026",
            "reason": (
                "Introduction of previously unseen counterparties combined "
                "with rapid fund movement was assessed as high risk and "
                "escalated for further investigation."
            ),
            "analyst": "K. Verma",
            "matching_factors": ["New counterparties", "Rapid movement", "Typology"],
            "differing_factors": ["Slightly lower transaction amount"],
        },
        {
            "id": "AML-0831",
            "similarity": 86,
            "decision": "ESCALATE",
            "pattern": "Behavioral change detected",
            "date": "18 Jul 2026",
            "reason": (
                "Significant deviation from the customer's 12-month "
                "transaction baseline was the primary driver of escalation."
            ),
            "analyst": "R. Sharma",
            "matching_factors": ["Behavioral deviation", "Typology"],
            "differing_factors": ["Different geography"],
        },
    ],
    "AML-1067": [
        {
            "id": "AML-0954",
            "similarity": 84,
            "decision": "ESCALATE",
            "pattern": "Structuring below threshold",
            "date": "22 Jul 2026",
            "reason": (
                "Deposit pattern was assessed as deliberate structuring "
                "to avoid reporting thresholds."
            ),
            "analyst": "K. Verma",
            "matching_factors": ["Deposit sizing", "Time intervals"],
            "differing_factors": ["Higher deposit count"],
        },
        {
            "id": "AML-0812",
            "similarity": 80,
            "decision": "CLEAR",
            "pattern": "Seasonal deposit pattern",
            "date": "05 Jul 2026",
            "reason": (
                "Deposits were reconciled against a documented seasonal "
                "cash business cycle and cleared."
            ),
            "analyst": "R. Sharma",
            "matching_factors": ["Deposit sizing"],
            "differing_factors": ["Verified business documentation on file"],
        },
    ],
    "AML-1066": [
        {
            "id": f"AML-{909 - i}",
            "similarity": 95 - i * 2,
            "decision": "CLEAR",
            "pattern": "Recurring payroll pattern",
            "date": _days_ago(20 + i * 15),
            "reason": "Matched declared payroll cycle and recipient list.",
            "analyst": random.choice(["R. Sharma", "K. Verma", "A. Iyer"]),
            "matching_factors": ["Customer segment", "Transaction frequency"],
            "differing_factors": ["Minor amount variance"],
        }
        for i in range(5)
    ],
}

# ---------------------------------------------------------------------------
# Customer memory
# ---------------------------------------------------------------------------

CUSTOMERS = {
    "CUST-3391": {
        "name": "Meridian Imports",
        "id": "CUST-3391",
        "segment": "Trading / Import-Export",
        "onboarded": "11 Feb 2023",
        "cleared_count": 4,
        "escalated_count": 2,
        "recurring_patterns": [
            "Quarterly bulk import settlements",
            "Occasional cross-border transfers to Singapore",
        ],
        "known_concerns": [
            "One prior escalation for undisclosed counterparty (resolved)",
        ],
        "observations": [
            "Customer has demonstrated consistent quarterly settlement "
            "behavior across 6 prior alerts, 4 of which were cleared.",
            "Recent 30-day activity shows a marked increase in transfer "
            "frequency versus the 12-month baseline.",
        ],
        "timeline": [
            {"date": "14 Aug 2026", "alert": "AML-1042", "decision": "CLEAR"},
            {"date": "02 Aug 2026", "alert": "AML-0987", "decision": "ESCALATE"},
            {"date": "18 Jul 2026", "alert": "AML-0831", "decision": "ESCALATE"},
            {"date": "30 May 2026", "alert": "AML-0705", "decision": "CLEAR"},
            {"date": "12 Mar 2026", "alert": "AML-0592", "decision": "CLEAR"},
        ],
    },
    "CUST-2210": {
        "name": "Nova Trading",
        "id": "CUST-2210",
        "segment": "Wholesale Trading",
        "onboarded": "04 Sep 2023",
        "cleared_count": 3,
        "escalated_count": 1,
        "recurring_patterns": ["Weekly cash deposits tied to retail turnover"],
        "known_concerns": ["Deposit sizing pattern flagged once previously"],
        "observations": [
            "Customer's deposit sizing has repeatedly clustered just below "
            "the reporting threshold across multiple review cycles.",
        ],
        "timeline": [
            {"date": "22 Jul 2026", "alert": "AML-0954", "decision": "ESCALATE"},
            {"date": "05 Jul 2026", "alert": "AML-0812", "decision": "CLEAR"},
            {"date": "19 Apr 2026", "alert": "AML-0640", "decision": "CLEAR"},
        ],
    },
    "CUST-1187": {
        "name": "Acme Retail",
        "id": "CUST-1187",
        "segment": "Retail / Payroll Services",
        "onboarded": "20 Jan 2022",
        "cleared_count": 5,
        "escalated_count": 0,
        "recurring_patterns": ["Bi-weekly payroll disbursement to fixed recipient list"],
        "known_concerns": [],
        "observations": [
            "Customer has demonstrated the same payroll pattern across five "
            "previously reviewed alerts, all cleared.",
        ],
        "timeline": [
            {"date": _days_ago(20 + i * 15), "alert": f"AML-{909 - i}", "decision": "CLEAR"}
            for i in range(5)
        ],
    },
}

# ---------------------------------------------------------------------------
# Analyst decisions / audit trail (grows as overrides happen)
# ---------------------------------------------------------------------------

AUDIT_TRAIL = [
    {
        "alert": "AML-1042",
        "ai_recommendation": "CLEAR",
        "confidence": 91,
        "precedents_used": ["AML-0705", "AML-0592"],
        "human_decision": "CLEAR",
        "override": False,
        "override_reason": None,
        "timestamp": "14 Aug 2026, 10:22",
        "memory_update": "Reinforced payroll-pattern precedent for CUST-3391",
    },
    {
        "alert": "AML-0987",
        "ai_recommendation": "ESCALATE",
        "confidence": 85,
        "precedents_used": ["AML-0831"],
        "human_decision": "ESCALATE",
        "override": False,
        "override_reason": None,
        "timestamp": "02 Aug 2026, 15:47",
        "memory_update": "New precedent stored: new-counterparty escalation",
    },
    {
        "alert": "AML-0954",
        "ai_recommendation": "CLEAR",
        "confidence": 68,
        "precedents_used": ["AML-0812"],
        "human_decision": "ESCALATE",
        "override": True,
        "override_reason": "Deposit clustering pattern judged deliberate despite prior clearance",
        "timestamp": "22 Jul 2026, 09:14",
        "memory_update": "Override recorded — precedent weighting adjusted for structuring cases",
    },
]

# ---------------------------------------------------------------------------
# Consistency audit — cases with high similarity but conflicting decisions
# ---------------------------------------------------------------------------

INCONSISTENCIES = [
    {
        "similarity": 91,
        "case_a": {
            "id": "AML-0987",
            "decision": "ESCALATE",
            "date": "02 Aug 2026",
            "analyst": "K. Verma",
            "reason": "New counterparty combined with rapid movement.",
        },
        "case_b": {
            "id": "AML-0831",
            "decision": "CLEAR",
            "date": "18 Jul 2026",
            "analyst": "A. Iyer",
            "reason": "Behavioral deviation judged explainable by seasonal activity.",
        },
        "matching_factors": ["Typology: Rapid Movement", "Amount range", "New counterparty flag"],
        "differing_factors": ["Geography", "Reviewing analyst"],
    },
    {
        "similarity": 88,
        "case_a": {
            "id": "AML-0954",
            "decision": "ESCALATE",
            "date": "22 Jul 2026",
            "analyst": "K. Verma",
            "reason": "Structuring pattern deemed deliberate.",
        },
        "case_b": {
            "id": "AML-0812",
            "decision": "CLEAR",
            "date": "05 Jul 2026",
            "analyst": "R. Sharma",
            "reason": "Seasonal cash business documentation on file.",
        },
        "matching_factors": ["Typology: Structuring", "Deposit sizing"],
        "differing_factors": ["Supporting documentation available"],
    },
]

# ---------------------------------------------------------------------------
# Evaluation metrics (DEMO / MOCK VALUES ONLY)
# ---------------------------------------------------------------------------

EVALUATION_METRICS = {
    "safe_clear_rate": {"without": 71, "with": 89},
    "false_clear_rate": {"without": 14, "with": 4},
    "illicit_recall": {"without": 62, "with": 85},
    "escalation_rate": {"without": 38, "with": 27},
    "avg_reasoning_time_sec": {"without": 340, "with": 95},
    "precedents_retrieved_avg": {"without": 0, "with": 3.4},
}

# ---------------------------------------------------------------------------
# Public interface functions — swap bodies for real implementations later
# ---------------------------------------------------------------------------

def get_alerts():
    """Return the current open alert queue."""
    return ALERTS


def get_alert(alert_id: str):
    return next((a for a in ALERTS if a["id"] == alert_id), None)


def get_precedents(alert_id: str):
    """Return historical precedent cases similar to the given alert."""
    return PRECEDENTS.get(alert_id, [])


def get_customer_memory(customer_id: str):
    """Return consolidated memory for a customer."""
    return CUSTOMERS.get(customer_id)


def get_customer_by_name(name: str):
    for c in CUSTOMERS.values():
        if c["name"] == name:
            return c
    return None


def get_typology_knowledge(typology: str):
    """Return typology knowledge / mental models."""
    return TYPOLOGIES.get(typology)


def get_pep_watchlist_status(customer_name: str):
    return PEP_WATCHLIST_STATUS.get(customer_name, {"pep": False, "watchlist": False})


def generate_decision(alert: dict, context: dict | None = None):
    """
    Generate an AI recommendation for an alert.
    MOCK IMPLEMENTATION — Member 2 will replace this with the real
    reasoning / evaluation pipeline.
    """
    precedents = get_precedents(alert["id"])
    escalate_votes = sum(1 for p in precedents if p["decision"] == "ESCALATE")
    clear_votes = sum(1 for p in precedents if p["decision"] == "CLEAR")

    recommendation = "ESCALATE" if escalate_votes >= clear_votes and alert["risk"] != "LOW" else "CLEAR"
    if alert["risk"] == "LOW":
        recommendation = "CLEAR"

    reason_map = {
        "Rapid Movement": (
            "Similar historical alerts involving new counterparties and rapid "
            "movement were frequently escalated by analysts."
        ),
        "Structuring": (
            "Deposit sizing and timing closely match prior structuring "
            "precedents that were escalated for further review."
        ),
        "Payroll": (
            "Transaction pattern is consistent with this customer's "
            "long-standing, repeatedly cleared payroll cycle."
        ),
    }

    return {
        "recommendation": recommendation,
        "confidence": alert["confidence"],
        "reason": reason_map.get(alert["typology"], "Pattern consistent with retrieved precedents."),
        "precedents_used": [p["id"] for p in precedents],
    }


def record_decision(alert_id: str, ai_recommendation: str, human_decision: str,
                     override_reason: str | None, analyst_note: str | None,
                     confidence: int, precedents_used: list[str]):
    """
    Record the analyst's final decision. MOCK IMPLEMENTATION — appends to the
    in-memory audit trail for this session so the UI can demonstrate the
    "memory gets updated" story. Member 1/2 will persist this for real.
    """
    entry = {
        "alert": alert_id,
        "ai_recommendation": ai_recommendation,
        "confidence": confidence,
        "precedents_used": precedents_used,
        "human_decision": human_decision,
        "override": ai_recommendation != human_decision,
        "override_reason": override_reason,
        "analyst_note": analyst_note,
        "timestamp": datetime.now().strftime("%d %b %Y, %H:%M"),
        "memory_update": (
            f"New precedent stored for future {get_alert(alert_id)['typology']} alerts"
            if ai_recommendation != human_decision
            else "Precedent reinforced — no override"
        ),
    }
    AUDIT_TRAIL.insert(0, entry)
    return entry


def get_audit_trail():
    return AUDIT_TRAIL


def get_inconsistencies():
    return INCONSISTENCIES


def get_evaluation_metrics():
    return EVALUATION_METRICS