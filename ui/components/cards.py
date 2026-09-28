"""Alert queue card component."""

import streamlit as st

from ui.styles.theme import COLORS, render_html, risk_color, risk_soft


def alert_card(alert: dict, on_analyze):
    risk = alert["risk"]
    color = risk_color(risk)
    soft = risk_soft(risk)

    with st.container(border=False):
        render_html(
            f"""
            <div style="
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-left: 3px solid {color};
                border-radius: 10px;
                padding: 1.1rem 1.3rem;
                margin-bottom: 0.6rem;
            ">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <div style="font-size:0.95rem; font-weight:700; color:{COLORS['text_primary']};">
                            {alert['id']} &nbsp;·&nbsp; {alert['customer']}
                        </div>
                        <div style="font-size:0.78rem; color:{COLORS['text_secondary']}; margin-top:3px;">
                            ₹{alert['amount']:,} &nbsp;·&nbsp; {alert['typology']}
                        </div>
                    </div>
                    <div style="
                        background:{soft}; color:{color};
                        border:1px solid {color}55; border-radius:6px;
                        padding: 3px 10px; font-size:0.7rem; font-weight:700; letter-spacing:0.04em;
                        white-space: nowrap;
                    ">{risk}</div>
                </div>

                <div style="margin-top:0.7rem; font-size:0.76rem; color:{COLORS['text_secondary']};">
                    <span style="color:{COLORS['text_muted']};">Signals:</span>
                    &nbsp;{" · ".join(alert['signals'])}
                </div>

                <div style="margin-top:0.7rem; display:flex; gap:1.4rem; font-size:0.76rem; color:{COLORS['text_secondary']};">
                    <span><b style="color:{COLORS['text_primary']};">{alert['precedent_count']}</b> precedents</span>
                    <span><b style="color:{COLORS['text_primary']};">{alert['confidence']}%</b> confidence</span>
                </div>
            </div>
            """
        )
        col1, col2 = st.columns([5, 1])
        with col2:
            if st.button(
                "Analyze →",
                key=f"analyze_{alert['id']}",
                use_container_width=True,
                type="primary"
            ):
                on_analyze(alert["id"])