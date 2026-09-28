def apply_guardrails(alert):
    """
    Apply mandatory safety rules.

    Returns:
        "ESCALATE" if a mandatory rule is triggered.
        None if normal AI reasoning can continue.
    """

    if alert.get("pep_match", False):
        return "ESCALATE"

    if alert.get("watchlist_match", False):
        return "ESCALATE"

    return None