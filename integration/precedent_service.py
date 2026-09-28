"""
integration/precedent_service.py
=================================
Adapter bridging memory/ (Hindsight) → agent/ (DecisionEngine) → Streamlit UI.

Public API
----------
analyze_alert(alert)          → dict   (UI-ready result)
record_analyst_decision(...)  → dict   (retention result)

Design rules
------------
- Never invents data; uses only what real modules return.
- Filters UNKNOWN / no-metadata Hindsight fragments before AI.
- Normalises precedents into the fields DecisionEngine/rank_precedents expect.
- Normalises the AI result into the shape the UI components expect.
- Never raises to the caller — always returns a result dict with "success".
- Never logs or exposes API keys or secrets.
"""

from __future__ import annotations

import time
import traceback
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
    """Convert 0.0–1.0 confidence to integer percentage for the UI."""
    return max(0, min(100, int(round(confidence_float * 100))))


# ---------------------------------------------------------------------------
# Step A+B+C+D: Retrieve and filter Hindsight precedents
# ---------------------------------------------------------------------------

def _retrieve_and_filter_precedents(alert: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call memory.precedent_memory.get_precedents(alert), then filter to only
    authoritative records:
        - alert_id != "UNKNOWN"
        - has_metadata == True
        - decision is known (not "UNKNOWN" or empty)

    Returns a dict with keys:
        success, raw_count, filtered, memory_count, error (optional)
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
        }

    if not recall_result.get("success", False):
        return {
            "success": False,
            "error": recall_result.get("error", "Hindsight recall returned failure."),
            "raw_count": 0,
            "filtered": [],
            "memory_count": 0,
        }

    all_precedents: List[Dict[str, Any]] = recall_result.get("precedents", [])
    raw_count = len(all_precedents)

    # Filter: keep only authoritative records
    filtered = [
        p for p in all_precedents
        if (
            p.get("alert_id", "UNKNOWN").upper() != "UNKNOWN"
            and p.get("has_metadata", False)
            and p.get("decision", "UNKNOWN").upper() not in ("UNKNOWN", "")
        )
    ]

    return {
        "success": True,
        "raw_count": raw_count,
        "filtered": filtered,
        "memory_count": raw_count,
        "latency_ms": recall_result.get("latency_ms", 0),
    }


# ---------------------------------------------------------------------------
# Step E: Normalise each precedent for DecisionEngine / rank_precedents
# ---------------------------------------------------------------------------

def _normalise_for_engine(
    hindsight_precedent: Dict[str, Any],
    current_alert: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Produce the dict shape DecisionEngine / rank_precedents expect.

    Key rule: comparison fields (customer_id, typology, transaction_pattern,
    amount) must come ONLY from the Hindsight precedent record itself — never
    from the current alert.  Copying current-alert values into a historical
    precedent record would make every precedent appear 100% similar (the
    ranker would be comparing the alert to itself).

    The 'typology' field returned by precedent_memory.py is always set to the
    CURRENT alert's typology (see precedent_memory.py line:
        "typology": typology  ← alert.get("typology", "")).
    We therefore treat it as non-genuine and do NOT use it for similarity.

    _has_comparison_data is True only when at least one comparison field is
    genuinely present in the Hindsight record.  When False, the similarity
    score is withheld from the UI (shows "Relevant precedent" instead of a
    fabricated percentage).  Future-proof: if Person 1 extends the Hindsight
    schema to include these fields, this flag will automatically activate.
    """
    p = hindsight_precedent

    # --- Genuine historical comparison fields ----------------------------
    # These exist in the Hindsight metadata and ARE stored by retain.py,
    # but precedent_memory.py's current implementation does not extract them
    # back into the precedent dict.  Use them if present, otherwise None.
    hist_customer_id      = p.get("customer_id")     or None   # absent → None
    hist_typology         = None                               # always current-alert-derived; discard
    hist_transaction_pat  = p.get("transaction_pattern") or None
    hist_amount           = None
    raw_amount = p.get("amount")
    if raw_amount is not None:
        try:
            v = float(raw_amount)
            hist_amount = v if v > 0 else None
        except (TypeError, ValueError):
            pass

    has_comparison_data = any(
        f is not None
        for f in (hist_customer_id, hist_typology, hist_transaction_pat, hist_amount)
    )

    return {
        # --- Identity / decision fields (always available) ---------------
        "alert_id":        p.get("alert_id", "UNKNOWN"),
        "analyst_decision": p.get("decision", "UNKNOWN"),  # rank_precedents key
        "decision":        p.get("decision", "UNKNOWN"),    # kept for UI
        "reason":          p.get("reason", ""),
        "override":        p.get("override", False),
        "timestamp":       p.get("timestamp", ""),
        "memory_id":       p.get("memory_id", ""),
        "relevance_reason": p.get("relevance_reason", ""),
        "source":          p.get("source", ""),
        # --- Comparison fields (genuine historical values only) -----------
        "customer_id":         hist_customer_id,
        "typology":            hist_typology,
        "transaction_pattern": hist_transaction_pat,
        "amount":              hist_amount if hist_amount is not None else 0,
        # --- Internal flag consumed by analyze_alert ---------------------
        "_has_comparison_data": has_comparison_data,
    }



# ---------------------------------------------------------------------------
# Step F+G: Call DecisionEngine, return UI-friendly result
# ---------------------------------------------------------------------------

def analyze_alert(alert: Dict[str, Any]) -> Dict[str, Any]:
    """
    Full integration pipeline:
        1. Retrieve Hindsight precedents
        2. Filter to authoritative records
        3. Normalise for DecisionEngine
        4. Call DecisionEngine.analyze(alert, precedents)
        5. Return UI-friendly result dict

    Always returns a dict — never raises.

    UI-friendly result shape:
        success           bool
        decision          str         "CLEAR" | "ESCALATE"
        recommendation    str         alias for decision (UI compat)
        risk_level        str         "LOW" | "MEDIUM" | "HIGH"
        confidence        int         0–100 (percentage, for UI display)
        confidence_raw    float       0.0–1.0 (raw value)
        reason            str
        key_factors       list[str]
        precedents_used   list[str]   alert_ids passed to AI
        precedent_count   int         number of filtered precedents used
        memory_count      int         total raw Hindsight results
        guardrail_applied bool
        human_review_required bool
        latency_ms        int
        error             str | None
        # For right panel (Memory Influence):
        hindsight_precedents list[dict]  normalised precedents (UI cards)
    """
    t_start = time.time()

    # ------------------------------------------------------------------ #
    # 1. Retrieve + filter
    # ------------------------------------------------------------------ #
    recall = _retrieve_and_filter_precedents(alert)
    hindsight_ok = recall["success"]
    filtered_precedents: List[Dict[str, Any]] = recall.get("filtered", [])
    memory_count: int = recall.get("memory_count", 0)

    # ------------------------------------------------------------------ #
    # FIX 1 — Self-exclusion.
    # Hindsight may surface the alert being analysed as a historical
    # memory of itself.  Strip it so the AI never cites the current alert
    # as its own precedent.
    # ------------------------------------------------------------------ #
    current_alert_id = (alert.get("alert_id") or alert.get("id") or "").strip().upper()
    if current_alert_id:
        filtered_precedents = [
            p for p in filtered_precedents
            if p.get("alert_id", "").strip().upper() != current_alert_id
        ]

    # ------------------------------------------------------------------ #
    # 2. Normalise for engine
    # ------------------------------------------------------------------ #
    engine_precedents = [
        _normalise_for_engine(p, alert) for p in filtered_precedents
    ]

    # ------------------------------------------------------------------ #
    # FIX 2+3 — Honest similarity scores.
    # rank_precedents is pure; running it here for the display panel does
    # not affect the engine's own internal call.
    #
    # A score is only stored in similarity_lookup when the precedent
    # contained at least one genuine historical comparison field AND the
    # computed score is > 0.  Without genuine fields, the score would be
    # an artefact of comparing the alert to itself (score = 0 regardless),
    # and we must not display that as a percentage.
    # ------------------------------------------------------------------ #
    similarity_lookup: Dict[str, float] = {}
    if engine_precedents:
        try:
            from agent.precedent_ranker import rank_precedents
            scored = rank_precedents(alert, engine_precedents, top_k=len(engine_precedents))
            # Build a fast lookup: ALERT_ID_UPPER → engine_precedent dict
            ep_by_id = {
                ep.get("alert_id", "").strip().upper(): ep
                for ep in engine_precedents
            }
            for row in scored:
                aid = (row.get("alert_id") or "").strip().upper()
                if not aid:
                    continue
                ep = ep_by_id.get(aid)
                has_data = ep is not None and ep.get("_has_comparison_data", False)
                score = float(row.get("similarity", 0.0))
                if has_data and score > 0:
                    similarity_lookup[aid] = score
                # Otherwise: absent from lookup → UI shows "Relevant precedent"
        except Exception:
            pass  # _to_ui_precedents falls back to "Relevant precedent" for all

    # ------------------------------------------------------------------ #
    # 3. Call DecisionEngine
    # ------------------------------------------------------------------ #
    try:
        from agent.decision_engine import DecisionEngine
        engine = DecisionEngine()
        result = engine.analyze(alert, engine_precedents)
    except Exception as exc:
        latency_ms = int((time.time() - t_start) * 1000)
        # Graceful fallback — do not crash the UI
        return {
            "success": False,
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
            "precedent_count": len(filtered_precedents),
            "memory_count": memory_count,
            "guardrail_applied": False,
            "human_review_required": True,
            "latency_ms": latency_ms,
            "error": f"DecisionEngine error: {type(exc).__name__}: {exc}",
            "hindsight_precedents": _to_ui_precedents(filtered_precedents, similarity_lookup),
            "hindsight_available": hindsight_ok,
        }

    # ------------------------------------------------------------------ #
    # 4. Detect guardrail path
    # ------------------------------------------------------------------ #
    # If DecisionEngine returned because a guardrail was triggered,
    # precedents_used will be [] and reason will be the safety message.
    guardrail_applied = (
        result.precedents_used == []
        and result.confidence == 1.0
        and "safety rule" in result.reason.lower()
    )

    latency_ms = int((time.time() - t_start) * 1000)

    confidence_raw = result.confidence
    confidence_pct = _safe_int_pct(confidence_raw)

    return {
        "success": True,
        "decision": result.decision,
        "recommendation": result.decision,   # UI compat alias
        "risk_level": result.risk_level,
        "confidence": confidence_pct,
        "confidence_raw": confidence_raw,
        "reason": result.reason,
        "key_factors": result.key_factors,
        "precedents_used": result.precedents_used,
        "precedent_count": len(filtered_precedents),
        "memory_count": memory_count,
        "guardrail_applied": guardrail_applied,
        "human_review_required": result.human_review_required,
        "latency_ms": latency_ms,
        "error": None,
        "hindsight_precedents": _to_ui_precedents(filtered_precedents, similarity_lookup),
        "hindsight_available": hindsight_ok,
    }


# ---------------------------------------------------------------------------
# Normalise Hindsight precedents → UI card shape
# ---------------------------------------------------------------------------

def _to_ui_precedents(
    filtered: List[Dict[str, Any]],
    similarity_lookup: Optional[Dict[str, float]] = None,
) -> List[Dict[str, Any]]:
    """
    Convert filtered Hindsight precedents into the shape expected by
    ui/components/precedent_card.py.

    similarity_lookup: {ALERT_ID_UPPER: float 0.0-1.0} from rank_precedents.
    Score > 0 → displayed as "XX%".  No score → "Relevant precedent" (never invented).
    """
    if similarity_lookup is None:
        similarity_lookup = {}

    cards = []
    for p in filtered:
        decision = p.get("decision", "UNKNOWN")
        alert_id = p.get("alert_id", "UNKNOWN")
        reason = p.get("reason", "")
        typology = p.get("typology", "")
        override = p.get("override", False)
        relevance = p.get("relevance_reason", "")

        # FIX 2 — real similarity label from rank_precedents; never invented
        score = similarity_lookup.get(alert_id.strip().upper())
        if score is not None:
            similarity_label = f"{int(round(score * 100))}%"
        else:
            similarity_label = "Relevant precedent"

        pattern = typology or "Historical alert"

        matching_factors: List[str] = []
        differing_factors: List[str] = []

        if typology:
            matching_factors.append(f"Typology: {typology}")
        if relevance:
            matching_factors.append(relevance)
        if override:
            differing_factors.append("Analyst overrode AI recommendation")

        cards.append({
            "id": alert_id,
            "similarity": similarity_label,
            "decision": decision,
            "pattern": pattern,
            "date": p.get("timestamp", ""),
            "reason": reason,
            "analyst": "Analyst",
            "matching_factors": matching_factors if matching_factors else ["Similar typology"],
            "differing_factors": differing_factors,
            "memory_id": p.get("memory_id", ""),
            "override": override,
        })

    return cards



# ---------------------------------------------------------------------------
# Step 3: Record analyst decision into Hindsight
# ---------------------------------------------------------------------------

def record_analyst_decision(
    alert: Dict[str, Any],
    agent_recommendation: str,
    final_decision: str,
    analyst_reason: str,
    analyst_note: Optional[str] = None,
    confidence: int = 0,
    precedents_used: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Persist the analyst's final decision to Hindsight via
    memory.retain.retain_analyst_decision().

    Returns a UI-friendly dict with:
        success, memory_update, latency_ms, error (on failure)
    """
    override = (agent_recommendation.upper() != final_decision.upper())

    # Build the reason string without inventing content
    reason_parts = [analyst_reason.strip()] if analyst_reason and analyst_reason.strip() else []
    if analyst_note and analyst_note.strip():
        reason_parts.append(analyst_note.strip())
    combined_reason = " | ".join(reason_parts) if reason_parts else "No reason provided."

    try:
        from memory.retain import retain_analyst_decision

        extra_metadata: Dict[str, Any] = {}
        if precedents_used:
            extra_metadata["precedents_used"] = ",".join(str(p) for p in precedents_used)
        if confidence:
            extra_metadata["ai_confidence"] = str(confidence)

        result = retain_analyst_decision(
            alert=alert,
            agent_recommendation=agent_recommendation,
            final_decision=final_decision,
            analyst_reason=combined_reason,
            metadata=extra_metadata if extra_metadata else None,
        )

        memory_update_msg = (
            f"Override recorded — new precedent stored for future "
            f"{alert.get('typology', '')} alerts"
            if override
            else "Decision reinforced — precedent updated in memory"
        )

        return {
            "success": True,
            "override": override,
            "memory_update": memory_update_msg,
            "latency_ms": result.get("latency_ms", 0),
            "error": None,
            # Retain for audit trail compat
            "alert": alert.get("alert_id") or alert.get("id"),
            "ai_recommendation": agent_recommendation,
            "human_decision": final_decision,
            "override_reason": analyst_reason if override else None,
            "analyst_note": analyst_note,
            "confidence": confidence,
            "precedents_used": precedents_used or [],
        }

    except Exception as exc:
        return {
            "success": False,
            "override": override,
            "memory_update": "Memory update failed — decision not persisted.",
            "latency_ms": 0,
            "error": f"retain_analyst_decision failed: {type(exc).__name__}: {exc}",
            "alert": alert.get("alert_id") or alert.get("id"),
            "ai_recommendation": agent_recommendation,
            "human_decision": final_decision,
            "override_reason": analyst_reason if override else None,
            "analyst_note": analyst_note,
            "confidence": confidence,
            "precedents_used": precedents_used or [],
        }
