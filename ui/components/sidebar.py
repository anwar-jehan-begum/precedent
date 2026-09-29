"""Enterprise-grade sidebar navigation for PRECEDENT."""

import streamlit as st
from data.live_alerts import using_dataset
from ui.styles.theme import COLORS, render_html

NAV_ITEMS = [
    ("◆  Command Center",  "command_center",  "WORKSPACE"),
    ("⚑  Alert Queue",      "alerts",           "WORKSPACE"),
    ("◈  Memory Explorer",  "memory",           "INTELLIGENCE"),
    ("⊕  Consistency Audit", "audit",           "INTELLIGENCE"),
    ("◉  Evaluation",       "evaluation",       "INTELLIGENCE"),
]


def render_sidebar():
    if "active_view" not in st.session_state:
        st.session_state.active_view = "command_center"

    with st.sidebar:
        # ── Brand ────────────────────────────────────────────
        ds_live = using_dataset()
        status_color = COLORS["risk_low"] if ds_live else COLORS["risk_medium"]
        status_label = "DATASET ACTIVE" if ds_live else "DEMO MODE"
        status_dot_style = (
            f"display:inline-block;width:6px;height:6px;"
            f"border-radius:50%;background:{status_color};"
            f"box-shadow:0 0 5px {status_color}80;"
        )

        render_html(
            f"""
            <div style="padding:1.4rem 1.1rem 1.1rem; border-bottom:1px solid {COLORS['border_soft']};">
                <div style="font-size:1.05rem;font-weight:800;letter-spacing:0.05em;
                            color:{COLORS['text_primary']};font-variant:small-caps;">
                    PRECEDENT
                </div>
                <div style="font-size:0.68rem;color:{COLORS['text_muted']};
                            margin-top:2px;letter-spacing:0.04em;">
                    AML Decision Intelligence
                </div>
                <div style="display:flex;align-items:center;gap:6px;margin-top:10px;">
                    <span style="{status_dot_style}"></span>
                    <span style="font-size:0.62rem;font-weight:600;letter-spacing:0.07em;
                                 color:{status_color};text-transform:uppercase;">
                        {status_label}
                    </span>
                </div>
            </div>
            """
        )

        # ── Navigation ───────────────────────────────────────
        active = st.session_state.active_view
        current_group = None

        for label, key, group in NAV_ITEMS:
            # Group header
            if group != current_group:
                current_group = group
                render_html(
                    f"""
                    <div style="padding:1.1rem 1.1rem 0.35rem;
                                font-size:0.6rem;font-weight:700;letter-spacing:0.1em;
                                color:{COLORS['text_faint']};text-transform:uppercase;">
                        {group}
                    </div>
                    """
                )

            is_active = active == key
            bg     = COLORS["surface_alt"] if is_active else "transparent"
            border = f"2px solid {COLORS['accent']}" if is_active else f"2px solid transparent"
            color  = COLORS["text_primary"] if is_active else COLORS["text_secondary"]

            render_html(
                f"""
                <div style="
                    margin: 1px 8px;
                    border-radius: 7px;
                    background: {bg};
                    border-left: {border};
                    padding: 0;
                " id="nav_wrap_{key}">
                </div>
                """
            )

            if st.button(
                label,
                key=f"nav_{key}",
                use_container_width=True,
            ):
                st.session_state.active_view = key
                if key == "alerts":
                    st.session_state.selected_alert = None
                st.rerun()

        # ── Footer ───────────────────────────────────────────
        render_html(
            f"""
            <div style="position:fixed;bottom:0;left:0;width:230px;
                        padding:0.8rem 1.2rem;
                        border-top:1px solid {COLORS['border_soft']};
                        background:{COLORS['bg_alt']};">
                <div style="font-size:0.62rem;color:{COLORS['text_faint']};
                            letter-spacing:0.04em;line-height:1.5;">
                    Institutional memory for every investigation.
                    <br>Hackathon Build · 2026
                </div>
            </div>
            """
        )