from agent.guardrails import apply_guardrails


normal_alert = {
    "pep_match": False,
    "watchlist_match": False
}

pep_alert = {
    "pep_match": True,
    "watchlist_match": False
}

watchlist_alert = {
    "pep_match": False,
    "watchlist_match": True
}


print("Normal:", apply_guardrails(normal_alert))
print("PEP:", apply_guardrails(pep_alert))
print("Watchlist:", apply_guardrails(watchlist_alert))