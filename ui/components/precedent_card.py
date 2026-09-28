"""Expandable precedent case card, used in Case Intelligence and Memory Explorer."""

import streamlit as st

from ui.styles.theme import COLORS, render_html


def precedent_card(precedent: dict, key_prefix: str = "prec"):
    decision = precedent["decision"]
    color = COLORS["risk_low"] if decision == "CLEAR" else COLORS["risk_medium"]

    header = (
        f"{precedent['id']}  ·  {precedent['similarity']}% similar  ·  {decision}"
    )

    with st.expander(header, expanded=False):
        render_html(
            f"""
            <div style="font-size:0.8rem; color:{COLORS['text_secondary']}; line-height:1.6;">
                <div style="margin-bottom:6px;">
                    <span style="color:{COLORS['text_muted']};">Pattern:</span>
                    <span style="color:{COLORS['text_primary']};"> {precedent['pattern']}</span>
                </div>
                <div style="margin-bottom:6px;">
                    <span style="color:{COLORS['text_muted']};">Decision:</span>
                    <span style="color:{color}; font-weight:700;"> {decision}</span>
                    <span style="color:{COLORS['text_muted']};"> by {precedent.get('analyst', 'Unknown')} on {precedent['date']}</span>
                </div>
                <div style="margin-bottom:6px;">
                    <span style="color:{COLORS['text_muted']};">Analyst reasoning:</span><br/>
                    <span style="color:{COLORS['text_primary']};">"{precedent['reason']}"</span>
                </div>
                <div style="margin-bottom:6px;">
                    <span style="color:{COLORS['text_muted']};">Matching factors:</span>
                    <span style="color:{COLORS['risk_low']};"> {", ".join(precedent.get('matching_factors', []))}</span>
                </div>
                <div>
                    <span style="color:{COLORS['text_muted']};">Differing factors:</span>
                    <span style="color:{COLORS['risk_medium']};"> {", ".join(precedent.get('differing_factors', []))}</span>
                </div>
            </div>
            """
        )