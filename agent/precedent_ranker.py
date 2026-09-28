def calculate_similarity(current_alert, precedent):
    score = 0.0

    if current_alert.get("customer_id") == precedent.get("customer_id"):
        score += 0.30

    if current_alert.get("typology") == precedent.get("typology"):
        score += 0.25

    if current_alert.get("transaction_pattern") == precedent.get("transaction_pattern"):
        score += 0.20

    current_amount = current_alert.get("amount", 0)
    previous_amount = precedent.get("amount", 0)

    if current_amount > 0 and previous_amount > 0:
        difference = abs(current_amount - previous_amount)
        average = (current_amount + previous_amount) / 2

        amount_similarity = 1 - (difference / average)

        if amount_similarity > 0:
            score += 0.25 * amount_similarity

    return round(min(score, 1.0), 2)


def rank_precedents(current_alert, precedents, top_k=3):

    ranked = []

    for precedent in precedents:

        similarity = calculate_similarity(
            current_alert,
            precedent
        )

        ranked.append({
            "alert_id": precedent.get("alert_id"),
            "decision": precedent.get("analyst_decision"),
            "reason": precedent.get("reason"),
            "similarity": similarity
        })

    ranked.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    return ranked[:top_k]