"""Custom sidebar navigation — replaces Streamlit's automatic multipage nav."""

import streamlit as st

from ui.styles.theme import COLORS, render_html

NAV_ITEMS = [
    ("Command Center", "command_center"),
    ("Alerts", "alerts"),
    ("Memory", "memory"),
    ("Consistency Audit", "audit"),
    ("Evaluation", "evaluation"),
]


def render_sidebar():
    if "active_view" not in st.session_state:
        st.session_state.active_view = "command_center"

    with st.sidebar:
        render_html(
            f"""
            <div style="padding: 0 0.25rem 1.25rem 0.25rem; border-bottom: 1px solid {COLORS['border_soft']};">
                <div style="font-size: 1.15rem; font-weight: 700; letter-spacing: 0.04em; color: {COLORS['text_primary']};">
                    PRECEDENT
                </div>
                <div style="font-size: 0.72rem; color: {COLORS['text_secondary']}; margin-top: 2px;">
                    AML Decision Intelligence
                </div>
                <div style="display:flex; align-items:center; gap:6px; margin-top: 10px;">
                    <span style="width:7px; height:7px; border-radius:50%; background:{COLORS['risk_low']}; display:inline-block; box-shadow: 0 0 6px {COLORS['risk_low']};"></span>
                    <span style="font-size: 0.68rem; color: {COLORS['text_secondary']}; letter-spacing: 0.05em;">SYSTEM OPERATIONAL</span>
                </div>
            </div>
            """
        )

        st.write("")

        for label, key in NAV_ITEMS:
            active = st.session_state.active_view == key
            if st.button(
                label,
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if active else "secondary",
            ):
                st.session_state.active_view = key
                if key == "alerts":
                    st.session_state.selected_alert = None
                st.rerun()

        render_html(
            f"""
            <div style="position: fixed; bottom: 1.5rem; padding: 0 0.25rem; color: {COLORS['text_muted']}; font-size: 0.68rem;">
                Institutional memory for every investigation.
            </div>
            """
        )