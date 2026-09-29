from typing import Dict, Any, List

from memory.recall import execute_recall


def _safe_float(value):
    """Convert a value to float without raising."""
    try:
        if value in (None, ""):
            return None

        number = float(value)

        return number if number > 0 else None

    except (TypeError, ValueError):
        return None


def _safe_bool(value) -> bool:
    """Convert common Hindsight metadata values to bool."""
    if isinstance(value, bool):
        return value

    return str(value).strip().lower() == "true"


def get_precedents(alert: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieve historical analyst decisions from Hindsight.

    Historical comparison fields are taken ONLY from the recalled
    Hindsight metadata. No fields are copied from the current alert
    into a historical precedent.
    """

    customer_id = alert.get("customer_id", "")
    typology = alert.get("typology", "")
    transaction_pattern = alert.get(
        "transaction_pattern",
        ""
    )

    query = (
        f"Previous alerts and analyst decisions for "
        f"customer {customer_id} involving typology "
        f"'{typology}' and transaction pattern "
        f"'{transaction_pattern}'."
    )

    tags = [
        f"customer:{customer_id}",
        f"typology:{str(typology).replace(' ', '_')}",
        "decision",
    ]

    recall_result = execute_recall(
        query=query,
        tags=tags,
        tags_match="any",
    )

    precedents: List[Dict[str, Any]] = []

    if recall_result.get("success") and recall_result.get("results"):

        for res in recall_result["results"]:

            text = (
                res.text
                if hasattr(res, "text")
                else str(res)
            )

            metadata = (
                getattr(res, "metadata", {}) or {}
            )

            # --------------------------------------------------
            # Only records with authoritative decision metadata
            # are treated as precedents.
            # --------------------------------------------------

            if (
                not metadata
                or "final_decision" not in metadata
            ):
                continue

            decision = str(
                metadata.get(
                    "final_decision",
                    "UNKNOWN",
                )
            ).upper()

            if decision not in {"CLEAR", "ESCALATE"}:
                continue

            alert_id = str(
                metadata.get(
                    "alert_id",
                    "UNKNOWN",
                )
            ).upper()

            if alert_id == "UNKNOWN":
                continue

            historical_customer_id = metadata.get(
                "customer_id"
            )

            historical_typology = metadata.get(
                "typology"
            )

            historical_pattern = metadata.get(
                "transaction_pattern"
            )

            historical_amount = _safe_float(
                metadata.get("amount")
            )

            historical_currency = metadata.get(
                "currency"
            )

            analyst_reason = str(
                metadata.get(
                    "analyst_reason",
                    text,
                )
            )

            timestamp = metadata.get(
                "timestamp"
            ) or getattr(
                res,
                "timestamp",
                "",
            )

            override = _safe_bool(
                metadata.get(
                    "override",
                    False,
                )
            )

            memory_id = getattr(
                res,
                "id",
                "UNKNOWN",
            )

            # --------------------------------------------------
            # Explain why this precedent was retrieved.
            # This uses historical data and current alert data,
            # but never modifies the historical values.
            # --------------------------------------------------

            matching_parts = []

            if (
                historical_customer_id
                and str(historical_customer_id)
                == str(customer_id)
            ):
                matching_parts.append(
                    "same customer"
                )

            if (
                historical_typology
                and str(historical_typology)
                == str(typology)
            ):
                matching_parts.append(
                    "same typology"
                )

            if (
                historical_pattern
                and str(historical_pattern)
                == str(transaction_pattern)
            ):
                matching_parts.append(
                    "same transaction pattern"
                )

            if matching_parts:
                relevance_reason = (
                    "Retrieved because of "
                    + ", ".join(matching_parts)
                )
            else:
                relevance_reason = (
                    "Similar historical AML decision"
                )

            precedent = {
                # Identity / decision
                "alert_id": alert_id,
                "decision": decision,
                "reason": analyst_reason,

                # Genuine historical comparison fields
                "customer_id": (
                    str(historical_customer_id)
                    if historical_customer_id
                    else None
                ),
                "typology": (
                    str(historical_typology)
                    if historical_typology
                    else None
                ),
                "transaction_pattern": (
                    str(historical_pattern)
                    if historical_pattern
                    else None
                ),
                "amount": historical_amount,
                "currency": (
                    str(historical_currency)
                    if historical_currency
                    else None
                ),

                # Other memory metadata
                "timestamp": (
                    str(timestamp)
                    if timestamp
                    else "UNKNOWN"
                ),
                "memory_id": str(memory_id),
                "source": text,
                "relevance_reason": relevance_reason,
                "override": override,

                # This means the record contains authoritative
                # historical metadata, NOT that every field exists.
                "has_metadata": True,
            }

            precedents.append(precedent)

    # ------------------------------------------------------
    # Deduplicate by alert_id.
    # Prefer the record containing more historical fields.
    # ------------------------------------------------------

    deduped: Dict[str, Dict[str, Any]] = {}

    for precedent in precedents:

        alert_id = precedent["alert_id"]

        existing = deduped.get(alert_id)

        if existing is None:
            deduped[alert_id] = precedent
            continue

        def field_count(item):
            fields = [
                "customer_id",
                "typology",
                "transaction_pattern",
                "amount",
                "currency",
                "timestamp",
                "reason",
            ]

            return sum(
                1
                for field in fields
                if item.get(field) not in (None, "")
            )

        if field_count(precedent) > field_count(existing):
            deduped[alert_id] = precedent

    final_precedents = list(
        deduped.values()
    )

    # ------------------------------------------------------
    # Hindsight failure
    # ------------------------------------------------------

    if not recall_result.get("success", False):

        return {
            "success": False,
            "error": recall_result.get(
                "error",
                "Unknown error during Hindsight recall",
            ),
            "alert_id": alert.get("alert_id"),
            "customer_id": customer_id,
            "precedents": [],
            "count": 0,
            "query": query,
            "evidence_available": False,
            "latency_ms": recall_result.get(
                "latency_ms",
                0,
            ),
            "trace_available": False,
        }

    # ------------------------------------------------------
    # Successful recall
    # ------------------------------------------------------

    return {
        "success": True,
        "alert_id": alert.get("alert_id"),
        "customer_id": customer_id,
        "precedents": final_precedents,
        "count": len(final_precedents),
        "query": query,
        "evidence_available": len(
            final_precedents
        ) > 0,
        "latency_ms": recall_result.get(
            "latency_ms",
            0,
        ),
        "trace_available": recall_result.get(
            "trace_available",
            False,
        ),
    }