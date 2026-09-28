"""Consistency Audit + Audit Trail view."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from data.mock_data import get_audit_trail
from ui.styles.theme import COLORS, render_html


# ---------------------------------------------------------------------------
# Live consistency detection from Hindsight
# ---------------------------------------------------------------------------

def _detect_live_inconsistencies():
    """
    Pull authoritative precedents from Hindsight and find pairs where:
      - the alert_id is different (not same case)
      - the decision differs (one CLEAR, one ESCALATE)
    Returns a list of inconsistency dicts in the UI schema.
    """
    try:
        from integration.precedent_service import _retrieve_and_filter_precedents
        synthetic = {
            "alert_id": "AUDIT-QUERY",
            "id":       "AUDIT-QUERY",
            "typology": "AML",
            "transaction_pattern": "AML",
            "customer_id": "",
            "amount": 0,
        }
        recall = _retrieve_and_filter_precedents(synthetic)
        if not recall.get("success"):
            return None, recall.get("error", "Hindsight unavailable")

        precedents = recall.get("filtered", [])
        if not precedents:
            return [], None

        # Find conflicting pairs
        conflicts = []
        seen_pairs: set = set()
        for i, a in enumerate(precedents):
            for j, b in enumerate(precedents):
                if i >= j:
                    continue
                aid = a.get("alert_id", "")
                bid = b.get("alert_id", "")
                if aid == bid:
                    continue
                pair_key = (min(aid, bid), max(aid, bid))
                if pair_key in seen_pairs:
                    continue
                dec_a = (a.get("decision") or "").upper()
                dec_b = (b.get("decision") or "").upper()
                if dec_a in ("CLEAR", "ESCALATE") and dec_b in ("CLEAR", "ESCALATE") and dec_a != dec_b:
                    seen_pairs.add(pair_key)
                    typ_a = a.get("typology", "")
                    typ_b = b.get("typology", "")
                    matching = []
                    if typ_a and typ_b and typ_a == typ_b:
                        matching.append(f"Typology: {typ_a}")
                    conflicts.append({
                        "similarity": "—",   # genuine similarity unavailable without comparison fields
                        "case_a": {
                            "id":       aid,
                            "decision": dec_a,
                            "date":     a.get("timestamp", "")[:10] if a.get("timestamp") else "",
                            "analyst":  "Analyst",
                            "reason":   a.get("reason", ""),
                        },
                        "case_b": {
                            "id":       bid,
                            "decision": dec_b,
                            "date":     b.get("timestamp", "")[:10] if b.get("timestamp") else "",
                            "analyst":  "Analyst",
                            "reason":   b.get("reason", ""),
                        },
                        "matching_factors":  matching or ["Historical AML alert"],
                        "differing_factors": ["Different analyst decision"],
                    })
                if len(conflicts) >= 5:   # cap for UI readability
                    break
            if len(conflicts) >= 5:
                break

        return conflicts, None

    except Exception as exc:
        return None, str(exc)


# ---------------------------------------------------------------------------
# Render helpers
# ---------------------------------------------------------------------------

def _render_inconsistency(item: dict, index: int):
    a, b = item["case_a"], item["case_b"]
    color_a = COLORS["risk_medium"] if a["decision"] == "ESCALATE" else COLORS["risk_low"]
    color_b = COLORS["risk_medium"] if b["decision"] == "ESCALATE" else COLORS["risk_low"]

    sim = item.get("similarity", "—")
    raw_sim = str(sim)
    if isinstance(sim, (int, float)):
        sim_label = f"{int(round(float(sim) * 100) if float(sim) <= 1 else sim)}% similar"
    elif raw_sim.rstrip().endswith("%"):
        sim_label = f"{raw_sim} similar"
    else:
        sim_label = None   # text label — omit from header

    base_header = f"{a['id']} → {a['decision']}  vs  {b['id']} → {b['decision']}"
    header = (
        f"Conflicting decisions  ·  {sim_label}  ·  {base_header}"
        if sim_label else
        f"Conflicting decisions  ·  {base_header}"
    )

    with st.expander(header):
        col1, col2 = st.columns(2)
        for col, case, color in [(col1, a, color_a), (col2, b, color_b)]:
            with col:
                render_html(
                    f"""
                    <div style="background:{COLORS['surface']};
                                border:1px solid {COLORS['border']};
                                border-top:2px solid {color};
                                border-radius:10px;padding:1rem;">
                        <div style="font-weight:700;color:{COLORS['text_primary']};">{case['id']}</div>
                        <div style="color:{color};font-weight:700;font-size:0.85rem;margin-top:4px;">{case['decision']}</div>
                        <div style="color:{COLORS['text_muted']};font-size:0.75rem;margin-top:4px;">{case['analyst']} · {case['date']}</div>
                        <div style="color:{COLORS['text_secondary']};font-size:0.8rem;margin-top:8px;font-style:italic;">"{case['reason']}"</div>
                    </div>
                    """
                )

        st.write("")
        col_m, col_d = st.columns(2)
        with col_m:
            st.markdown("**Matching factors**")
            for f in item["matching_factors"]:
                st.write(f"• {f}")
        with col_d:
            st.markdown("**Differing factors**")
            for f in item["differing_factors"]:
                st.write(f"• {f}")


def _render_audit_table():
    trail = get_audit_trail()
    if not trail:
        st.caption("No audit events recorded yet this session.")
        return

    rows = []
    for e in trail:
        rows.append(
            {
                "Alert":              e["alert"],
                "AI Recommendation":  e["ai_recommendation"],
                "Confidence":         f"{e['confidence']}%",
                "Precedents Used":    ", ".join(e["precedents_used"]),
                "Human Decision":     e["human_decision"],
                "Override":           "Yes" if e["override"] else "No",
                "Override Reason":    e.get("override_reason") or "—",
                "Timestamp":          e["timestamp"],
                "Memory Update":      e["memory_update"],
            }
        )
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render():
    render_html(
        f"""
        <div style="margin-bottom:1.1rem;">
            <div style="font-size:1.4rem;font-weight:700;
                        color:{COLORS['text_primary']};">Consistency Audit</div>
            <div style="font-size:0.82rem;color:{COLORS['text_secondary']};">
                Cases with conflicting analyst decisions retrieved from Hindsight.
                Similarity scores unavailable until historical field schema is extended.
            </div>
        </div>
        """
    )

    with st.spinner("Querying Hindsight for conflicting decisions…"):
        conflicts, error = _detect_live_inconsistencies()

    if error:
        st.warning(
            f"Could not query Hindsight for conflicts: {error}. "
            "Check HINDSIGHT_API_KEY and network access.",
            icon="⚠️",
        )
    elif conflicts is None:
        st.info("No Hindsight data available.", icon="ℹ️")
    elif len(conflicts) == 0:
        render_html(
            f"""
            <div style="background:{COLORS['surface']};
                        border:1px solid {COLORS['border']};
                        border-radius:9px;padding:0.85rem 1rem;
                        color:{COLORS['text_muted']};font-size:0.8rem;
                        margin-bottom:1rem;">
                No conflicting decisions found in current Hindsight data.
                Record more analyst decisions to build a richer precedent history.
            </div>
            """
        )
    else:
        st.caption(f"{len(conflicts)} potential inconsistenc{'y' if len(conflicts)==1 else 'ies'} found in Hindsight")
        for i, item in enumerate(conflicts):
            _render_inconsistency(item, i)

    st.write("")
    st.markdown("### Audit Trail")
    st.caption("Full record of every AI recommendation and human decision, for compliance review.")
    _render_audit_table()