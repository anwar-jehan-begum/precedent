"""Premium precedent case card — Case Intelligence and Memory Explorer."""

import streamlit as st
from ui.styles.theme import COLORS, render_html


def precedent_card(precedent: dict, key_prefix: str = "prec"):
    decision   = precedent.get("decision", "UNKNOWN")
    is_clear   = decision == "CLEAR"
    dec_color  = COLORS["risk_low"] if is_clear else COLORS["risk_medium"]
    is_override = precedent.get("override", False)

    # ── Similarity label ───────────────────────────────────────────────────
    # similarity is either a numeric label like "92%" (from real ranker data)
    # or a text label like "Relevant precedent". NEVER append "% similar"
    # blindly — that caused "Relevant precedent% similar".
    raw_sim = str(precedent.get("similarity", "Relevant precedent"))
    if raw_sim.rstrip().endswith("%"):
        sim_label = f"{raw_sim} similar"
    else:
        sim_label = raw_sim   # text label — used verbatim

    # ── Override badge ─────────────────────────────────────────────────────
    override_badge = (
        f'<span style="font-size:0.58rem;font-weight:700;letter-spacing:0.06em;'
        f'background:{COLORS["risk_medium"]}14;color:{COLORS["risk_medium"]};'
        f'border:1px solid {COLORS["risk_medium"]}40;border-radius:4px;'
        f'padding:1px 5px;margin-left:5px;">OVERRIDE</span>'
        if is_override else ""
    )

    # ── Expander header ────────────────────────────────────────────────────
    alert_id   = precedent.get("id", "UNKNOWN")
    header_txt = f"{alert_id}  ·  {sim_label}  ·  {decision}"

    with st.expander(header_txt, expanded=False):
        # Decision + override badge row
        render_html(
            f"""
            <div style="
                display:flex;align-items:center;gap:8px;
                margin-bottom:10px;padding-bottom:8px;
                border-bottom:1px solid {COLORS['border_soft']};
            ">
                <span style="
                    background:{dec_color}14;color:{dec_color};
                    border:1px solid {dec_color}44;border-radius:5px;
                    padding:2px 8px;font-size:0.68rem;font-weight:700;
                    letter-spacing:0.05em;">
                    {decision}
                </span>
                {override_badge}
                <span style="font-size:0.68rem;color:{COLORS['text_muted']};
                             margin-left:auto;">
                    {precedent.get('date', '')}
                </span>
            </div>
            """
        )

        # Key/value detail rows
        rows = []
        if precedent.get("pattern"):
            rows.append(("Transaction pattern", precedent["pattern"]))
        if precedent.get("reason"):
            rows.append(("Analyst reasoning", precedent["reason"]))
        if precedent.get("matching_factors"):
            rows.append(("Matching factors",
                         ", ".join(precedent["matching_factors"])))
        if precedent.get("differing_factors"):
            rows.append(("Differing factors",
                         ", ".join(precedent["differing_factors"])))

        for label, value in rows:
            render_html(
                f"""
                <div style="
                    padding:4px 0;
                    font-size:0.77rem;
                    line-height:1.5;
                ">
                    <span style="color:{COLORS['text_muted']};
                                 font-size:0.68rem;font-weight:600;
                                 letter-spacing:0.04em;text-transform:uppercase;">
                        {label}
                    </span><br>
                    <span style="color:{COLORS['text_secondary']};">{value}</span>
                </div>
                """
            )