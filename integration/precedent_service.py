"""
integration/precedent_service.py
=================================
Adapter bridging memory/ (Hindsight) -> agent/ (DecisionEngine) -> Streamlit UI.

Public API
----------
analyze_alert(alert)          -> dict   (UI-ready result)
record_analyst_decision(...)  -> dict   (retention result)

Design rules
------------
- Never invents data; uses only what real modules return.
- Filters UNKNOWN / no-metadata Hindsight fragments before AI.
- Normalises precedents into the fields DecisionEngine/rank_precedents expect.
- Normalises the AI result into the shape the UI components expect.
- Never raises to the caller - always returns a result dict with "success".
- Never logs or exposes API keys or secrets.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int_pct(confidence_float: float) -> int:
    """Convert 0.0-1.0 confidence to integer percentage for the UI."""
    return max(
        0,
        min(
            100,
            int(round(confidence_float * 100))
        )
    )


# ---------------------------------------------------------------------------
# Step A+B+C+D: Retrieve and filter Hindsight precedents
# ---------------------------------------------------------------------------

def _retrieve_and_filter_precedents(
    alert: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Call memory.precedent_memory.get_precedents(alert), then filter to only
    authoritative historical decision records.

    Filters out:
        - UNKNOWN alert IDs
        - records without authoritative metadata
        - UNKNOWN / empty decisions

    Returns:
        success
        raw_count
        filtered
        memory_count
        latency_ms
        error (when unsuccessful)
    """

    try:
        from memory.precedent_memory import get_precedents

        recall_result = get_precedents(alert)

    except Exception as exc:
        return {
            "success": False,
            "error": f"Hindsight recall failed: {exc}",
            "raw_count": 0,
            "filtered": [],
            "memory_count": 0,
            "latency_ms": 0,
        }

    if not recall_result.get("success", False):
        return {
            "success": False,
            "error": recall_result.get(
                "error",
                "Hindsight recall returned failure."
            ),
            "raw_count": 0,
            "filtered": [],
            "memory_count": 0,
            "latency_ms": recall_result.get(
                "latency_ms",
                0
            ),
        }

    all_precedents: List[Dict[str, Any]] = (
        recall_result.get("precedents", [])
    )

    raw_count = len(all_precedents)

    # Keep only authoritative historical decisions.
    filtered = [
        p
        for p in all_precedents
        if (
            str(
                p.get("alert_id", "UNKNOWN")
            ).upper()
            != "UNKNOWN"
            and p.get("has_metadata", False)
            and str(
                p.get("decision", "UNKNOWN")
            ).upper()
            not in ("UNKNOWN", "")
        )
    ]

    return {
        "success": True,
        "raw_count": raw_count,
        "filtered": filtered,
        "memory_count": raw_count,
        "latency_ms": recall_result.get(
            "latency_ms",
            0
        ),
    }


# ---------------------------------------------------------------------------
# Step E: Normalise each precedent for DecisionEngine / rank_precedents
# ---------------------------------------------------------------------------

def _normalise_for_engine(
    hindsight_precedent: Dict[str, Any],
    current_alert: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convert a Hindsight precedent into the structure expected by the
    precedent ranker and DecisionEngine.

    CRITICAL RULE:
    Every historical comparison field comes ONLY from the recalled
    Hindsight precedent.

    Never copy customer_id, typology, transaction_pattern, amount, etc.
    from the current alert into a historical precedent.

    This prevents fabricated similarity scores.

    Historical comparison fields used when available:
        customer_id
        typology
        transaction_pattern
        amount
    """

    p = hindsight_precedent

    # ------------------------------------------------------------------
    # Genuine historical fields from Hindsight
    # ------------------------------------------------------------------

    historical_customer_id = (
        p.get("customer_id")
        or None
    )

    historical_typology = (
        p.get("typology")
        or None
    )

    historical_pattern = (
        p.get("transaction_pattern")
        or None
    )

    historical_amount = None

    raw_amount = p.get("amount")

    if raw_amount not in (None, ""):
        try:
            value = float(raw_amount)

            if value > 0:
                historical_amount = value

        except (TypeError, ValueError):
            historical_amount = None

    # ------------------------------------------------------------------
    # A genuine historical comparison record exists when at least one
    # historical comparison field is present.
    # ------------------------------------------------------------------

    has_comparison_data = any(
        value is not None
        for value in (
            historical_customer_id,
            historical_typology,
            historical_pattern,
            historical_amount,
        )
    )

    return {
        # --------------------------------------------------------------
        # Identity and decision information
        # --------------------------------------------------------------

        "alert_id": p.get(
            "alert_id",
            "UNKNOWN"
        ),

        "analyst_decision": p.get(
            "decision",
            "UNKNOWN"
        ),

        "decision": p.get(
            "decision",
            "UNKNOWN"
        ),

        "reason": p.get(
            "reason",
            ""
        ),

        "override": p.get(
            "override",
            False
        ),

        "timestamp": p.get(
            "timestamp",
            ""
        ),

        "memory_id": p.get(
            "memory_id",
            ""
        ),

        "relevance_reason": p.get(
            "relevance_reason",
            ""
        ),

        "source": p.get(
            "source",
            ""
        ),

        # --------------------------------------------------------------
        # REAL historical comparison fields
        # --------------------------------------------------------------

        "customer_id": historical_customer_id,

        "typology": historical_typology,

        "transaction_pattern": historical_pattern,

        "amount": (
            historical_amount
            if historical_amount is not None
            else 0
        ),

        # --------------------------------------------------------------
        # Internal flag used for honest similarity display
        # --------------------------------------------------------------

        "_has_comparison_data": has_comparison_data,
    }


# ---------------------------------------------------------------------------
# Step F+G: Call DecisionEngine, return UI-friendly result
# ---------------------------------------------------------------------------

def analyze_alert(
    alert: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Full PRECEDENT integration pipeline:

        1. Retrieve Hindsight precedents
        2. Filter authoritative precedents
        3. Normalize historical fields
        4. Exclude current alert from its own precedents
        5. Rank precedents for UI / AI
        6. Call DecisionEngine
        7. Return UI-friendly result

    Always returns a dict.
    """

    t_start = time.time()

    # ------------------------------------------------------------------
    # 1. Retrieve + filter
    # ------------------------------------------------------------------

    recall = _retrieve_and_filter_precedents(alert)

    hindsight_ok = recall.get(
        "success",
        False
    )

    filtered_precedents: List[Dict[str, Any]] = (
        recall.get(
            "filtered",
            []
        )
    )

    memory_count = int(
        recall.get(
            "memory_count",
            0
        )
    )

    # ------------------------------------------------------------------
    # 2. Self-exclusion
    #
    # Never allow the alert currently being analysed to appear as its
    # own historical precedent.
    # ------------------------------------------------------------------

    current_alert_id = str(
        alert.get("alert_id")
        or alert.get("id")
        or ""
    ).strip().upper()

    if current_alert_id:
        filtered_precedents = [
            precedent
            for precedent in filtered_precedents
            if str(
                precedent.get(
                    "alert_id",
                    ""
                )
            ).strip().upper()
            != current_alert_id
        ]

    # ------------------------------------------------------------------
    # 3. Normalize for DecisionEngine
    # ------------------------------------------------------------------

    engine_precedents = [
        _normalise_for_engine(
            precedent,
            alert
        )
        for precedent in filtered_precedents
    ]

    # ------------------------------------------------------------------
    # 4. Calculate honest similarity values for the UI
    #
    # A percentage is displayed only when historical comparison fields
    # genuinely exist.
    # ------------------------------------------------------------------

    similarity_lookup: Dict[str, float] = {}

    if engine_precedents:

        try:
            from agent.precedent_ranker import rank_precedents

            scored = rank_precedents(
                alert,
                engine_precedents,
                top_k=len(engine_precedents)
            )

            ep_by_id = {
                str(
                    precedent.get(
                        "alert_id",
                        ""
                    )
                ).strip().upper(): precedent
                for precedent in engine_precedents
            }

            for row in scored:

                alert_id = str(
                    row.get(
                        "alert_id",
                        ""
                    )
                ).strip().upper()

                if not alert_id:
                    continue

                precedent = ep_by_id.get(
                    alert_id
                )

                has_data = (
                    precedent is not None
                    and precedent.get(
                        "_has_comparison_data",
                        False
                    )
                )

                score = _safe_float(
                    row.get(
                        "similarity",
                        0.0
                    ),
                    0.0
                )

                if has_data and score > 0:
                    similarity_lookup[
                        alert_id
                    ] = score

        except Exception:
            # Never fabricate a similarity score if ranking fails.
            similarity_lookup = {}

    # ------------------------------------------------------------------
    # 5. Call DecisionEngine
    # ------------------------------------------------------------------

    try:

        from agent.decision_engine import DecisionEngine

        engine = DecisionEngine()

        result = engine.analyze(
            alert,
            engine_precedents
        )

    except Exception as exc:

        latency_ms = int(
            (time.time() - t_start)
            * 1000
        )

        return {
            "success": False,

            # This is a safe UI state when analysis fails.
            "decision": "ESCALATE",

            "recommendation": "ESCALATE",

            "risk_level": "HIGH",

            "confidence": 0,

            "confidence_raw": 0.0,

            "reason": (
                "AI analysis could not be completed. "
                "This alert requires direct human analyst review."
            ),

            "key_factors": [],

            "precedents_used": [],

            "precedent_count": len(
                filtered_precedents
            ),

            "memory_count": memory_count,

            "guardrail_applied": False,

            "human_review_required": True,

            "latency_ms": latency_ms,

            "error": (
                f"DecisionEngine error: "
                f"{type(exc).__name__}: {exc}"
            ),

            "hindsight_precedents": (
                _to_ui_precedents(
                    filtered_precedents,
                    similarity_lookup
                )
            ),

            "hindsight_available": hindsight_ok,
        }

    # ------------------------------------------------------------------
    # 6. Detect deterministic guardrail path
    # ------------------------------------------------------------------

    guardrail_applied = (
        result.precedents_used == []
        and result.confidence == 1.0
        and "safety rule"
        in result.reason.lower()
    )

    # ------------------------------------------------------------------
    # 7. Normalize confidence
    # ------------------------------------------------------------------

    latency_ms = int(
        (time.time() - t_start)
        * 1000
    )

    confidence_raw = _safe_float(
        result.confidence,
        0.0
    )

    confidence_pct = _safe_int_pct(
        confidence_raw
    )

    # ------------------------------------------------------------------
    # 8. UI result
    # ------------------------------------------------------------------

    return {
        "success": True,

        "decision": result.decision,

        "recommendation": result.decision,

        "risk_level": result.risk_level,

        "confidence": confidence_pct,

        "confidence_raw": confidence_raw,

        "reason": result.reason,

        "key_factors": result.key_factors,

        "precedents_used": result.precedents_used,

        "precedent_count": len(
            filtered_precedents
        ),

        "memory_count": memory_count,

        "guardrail_applied": guardrail_applied,

        "human_review_required": (
            result.human_review_required
        ),

        "latency_ms": latency_ms,

        "error": None,

        "hindsight_precedents": (
            _to_ui_precedents(
                filtered_precedents,
                similarity_lookup
            )
        ),

        "hindsight_available": hindsight_ok,
    }


# ---------------------------------------------------------------------------
# Normalise Hindsight precedents -> UI card shape
# ---------------------------------------------------------------------------

def _to_ui_precedents(
    filtered: List[Dict[str, Any]],
    similarity_lookup: Optional[
        Dict[str, float]
    ] = None,
) -> List[Dict[str, Any]]:
    """
    Convert filtered Hindsight precedents into the shape expected by
    ui/components/precedent_card.py.

    A similarity percentage is shown only when a real ranking score exists.

    Otherwise:
        "Relevant precedent"

    This prevents fabricated percentages.
    """

    if similarity_lookup is None:
        similarity_lookup = {}

    cards = []

    for precedent in filtered:

        decision = precedent.get(
            "decision",
            "UNKNOWN"
        )

        alert_id = str(
            precedent.get(
                "alert_id",
                "UNKNOWN"
            )
        )

        reason = precedent.get(
            "reason",
            ""
        )

        typology = precedent.get(
            "typology",
            ""
        )

        override = precedent.get(
            "override",
            False
        )

        relevance = precedent.get(
            "relevance_reason",
            ""
        )

        # --------------------------------------------------------------
        # Honest similarity label
        # --------------------------------------------------------------

        score = similarity_lookup.get(
            alert_id.strip().upper()
        )

        if score is not None:

            similarity_label = (
                f"{int(round(score * 100))}%"
            )

        else:

            similarity_label = (
                "Relevant precedent"
            )

        # --------------------------------------------------------------
        # Matching / differing factors
        # --------------------------------------------------------------

        matching_factors: List[str] = []

        differing_factors: List[str] = []

        if typology:

            matching_factors.append(
                f"Typology: {typology}"
            )

        if relevance:

            matching_factors.append(
                relevance
            )

        if override:

            differing_factors.append(
                "Analyst overrode AI recommendation"
            )

        if not matching_factors:

            matching_factors.append(
                "Historical analyst decision"
            )

        # --------------------------------------------------------------
        # UI card
        # --------------------------------------------------------------

        cards.append(
            {
                "id": alert_id,

                "similarity": similarity_label,

                "decision": decision,

                "pattern": (
                    typology
                    or "Historical alert"
                ),

                "date": precedent.get(
                    "timestamp",
                    ""
                ),

                "reason": reason,

                "analyst": "Analyst",

                "matching_factors": matching_factors,

                "differing_factors": differing_factors,

                "memory_id": precedent.get(
                    "memory_id",
                    ""
                ),

                "override": override,
            }
        )

    return cards


# ---------------------------------------------------------------------------
# Record analyst decision into Hindsight
# ---------------------------------------------------------------------------

def record_analyst_decision(
    alert: Dict[str, Any],
    agent_recommendation: str,
    final_decision: str,
    analyst_reason: str,
    analyst_note: Optional[str] = None,
    confidence: int = 0,
    precedents_used: Optional[
        List[str]
    ] = None,
) -> Dict[str, Any]:
    """
    Persist the analyst's final decision to Hindsight via
    memory.retain.retain_analyst_decision().

    The human analyst remains the final decision maker.
    """

    override = (
        agent_recommendation.upper()
        != final_decision.upper()
    )

    # --------------------------------------------------------------
    # Combine analyst reason + optional note
    # --------------------------------------------------------------

    reason_parts = []

    if (
        analyst_reason
        and analyst_reason.strip()
    ):
        reason_parts.append(
            analyst_reason.strip()
        )

    if (
        analyst_note
        and analyst_note.strip()
    ):
        reason_parts.append(
            analyst_note.strip()
        )

    combined_reason = (
        " | ".join(reason_parts)
        if reason_parts
        else "No reason provided."
    )

    try:

        from memory.retain import (
            retain_analyst_decision
        )

        extra_metadata: Dict[
            str,
            Any
        ] = {}

        if precedents_used:

            extra_metadata[
                "precedents_used"
            ] = ",".join(
                str(p)
                for p in precedents_used
            )

        if confidence:

            extra_metadata[
                "ai_confidence"
            ] = str(confidence)

        result = retain_analyst_decision(
            alert=alert,
            agent_recommendation=(
                agent_recommendation
            ),
            final_decision=final_decision,
            analyst_reason=combined_reason,
            metadata=(
                extra_metadata
                if extra_metadata
                else None
            ),
        )

        # ----------------------------------------------------------
        # Learning message
        # ----------------------------------------------------------

        memory_update_msg = (
            (
                f"Override recorded - new precedent stored "
                f"for future {alert.get('typology', '')} alerts"
            )
            if override
            else
            "Decision reinforced - precedent updated in memory"
        )

        return {
            "success": True,

            "override": override,

            "memory_update": memory_update_msg,

            "latency_ms": result.get(
                "latency_ms",
                0
            ),

            "error": None,

            # Audit trail compatibility
            "alert": (
                alert.get("alert_id")
                or alert.get("id")
            ),

            "ai_recommendation": (
                agent_recommendation
            ),

            "human_decision": final_decision,

            "override_reason": (
                analyst_reason
                if override
                else None
            ),

            "analyst_note": analyst_note,

            "confidence": confidence,

            "precedents_used": (
                precedents_used
                or []
            ),
        }

    except Exception as exc:

        return {
            "success": False,

            "override": override,

            "memory_update": (
                "Memory update failed - "
                "decision not persisted."
            ),

            "latency_ms": 0,

            "error": (
                "retain_analyst_decision failed: "
                f"{type(exc).__name__}: {exc}"
            ),

            "alert": (
                alert.get("alert_id")
                or alert.get("id")
            ),

            "ai_recommendation": (
                agent_recommendation
            ),

            "human_decision": final_decision,

            "override_reason": (
                analyst_reason
                if override
                else None
            ),

            "analyst_note": analyst_note,

            "confidence": confidence,

            "precedents_used": (
                precedents_used
                or []
            ),
        }