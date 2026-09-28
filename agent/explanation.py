def format_decision_explanation(result):
    lines = []

    lines.append(
        f"Recommendation: {result.decision}"
    )

    lines.append(
        f"Risk level: {result.risk_level}"
    )

    lines.append(
        f"Confidence: {result.confidence:.2f}"
    )

    lines.append("")

    lines.append("Why:")
    lines.append(result.reason)

    if result.key_factors:
        lines.append("")
        lines.append("Key factors:")

        for factor in result.key_factors:
            lines.append(f"- {factor}")

    if result.precedents_used:
        lines.append("")
        lines.append("Precedents used:")

        for precedent in result.precedents_used:
            lines.append(f"- {precedent}")

    lines.append("")

    lines.append(
        f"Human review required: "
        f"{result.human_review_required}"
    )

    return "\n".join(lines)