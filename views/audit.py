"""Consistency Audit + Audit Trail view."""

import pandas as pd
import streamlit as st

from data.mock_data import get_audit_trail, get_inconsistencies
from ui.styles.theme import COLORS, render_html


def render():
    render_html(
        f"""
        <div style="margin-bottom:1.1rem;">
            <div style="font-size:1.4rem; font-weight:700; color:{COLORS['text_primary']};">Consistency Audit</div>
            <div style="font-size:0.82rem; color:{COLORS['text_secondary']};">
                Cases with high similarity but conflicting analyst decisions. Demo data — not a
                claim about actual model or analyst performance.
            </div>
        </div>
        """
    )

    inconsistencies = get_inconsistencies()

    for i, item in enumerate(inconsistencies):
        _render_inconsistency(item, i)

    st.write("")
    st.markdown("### Audit Trail")
    st.caption("Full record of every AI recommendation and human decision, for compliance review.")
    _render_audit_table()


def _render_inconsistency(item: dict, index: int):
    a, b = item["case_a"], item["case_b"]
    color_a = COLORS["risk_medium"] if a["decision"] == "ESCALATE" else COLORS["risk_low"]
    color_b = COLORS["risk_medium"] if b["decision"] == "ESCALATE" else COLORS["risk_low"]

    header = f"Potential inconsistency · {item['similarity']}% similar · {a['id']} → {a['decision']}  vs  {b['id']} → {b['decision']}"

    with st.expander(header):
        col1, col2 = st.columns(2)
        for col, case, color in [(col1, a, color_a), (col2, b, color_b)]:
            with col:
                render_html(
                    f"""
                    <div style="background:{COLORS['surface']}; border:1px solid {COLORS['border']}; border-top:2px solid {color}; border-radius:10px; padding:1rem;">
                        <div style="font-weight:700; color:{COLORS['text_primary']};">{case['id']}</div>
                        <div style="color:{color}; font-weight:700; font-size:0.85rem; margin-top:4px;">{case['decision']}</div>
                        <div style="color:{COLORS['text_muted']}; font-size:0.75rem; margin-top:4px;">{case['analyst']} · {case['date']}</div>
                        <div style="color:{COLORS['text_secondary']}; font-size:0.8rem; margin-top:8px; font-style:italic;">"{case['reason']}"</div>
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
                "Alert": e["alert"],
                "AI Recommendation": e["ai_recommendation"],
                "Confidence": f"{e['confidence']}%",
                "Precedents Used": ", ".join(e["precedents_used"]),
                "Human Decision": e["human_decision"],
                "Override": "Yes" if e["override"] else "No",
                "Override Reason": e.get("override_reason") or "—",
                "Timestamp": e["timestamp"],
                "Memory Update": e["memory_update"],
            }
        )
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)