"""
PRECEDENT — AML Decision Intelligence
Member 3 — Product + UI + Demo (frontend shell, mock data)

Run with:
    streamlit run app.py
"""

import streamlit as st

from data.live_alerts import get_alerts, using_dataset
from data.mock_data import get_audit_trail
from ui.components.metrics import metric_row
from ui.components.sidebar import render_sidebar
from ui.styles.theme import COLORS, inject_global_css, render_html
from views import alerts as alerts_view
from views import audit as audit_view
from views import evaluation as evaluation_view
from views import memory as memory_view

st.set_page_config(
    page_title="PRECEDENT — AML Decision Intelligence",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_css()

if "active_view" not in st.session_state:
    st.session_state.active_view = "command_center"
if "selected_alert" not in st.session_state:
    st.session_state.selected_alert = None

render_sidebar()


def _render_dataset_blocker():
    st.error(
        "**FINAL BLOCKER — Dataset missing**\n\n"
        "The HI-Small dataset is not present in this workspace.\n\n"
        "**Required file:** `data/HI-Small/HI-Small_Trans.csv`\n\n"
        "Place the file at that path and restart Streamlit. "
        "All code is ready — no other change needed to activate the real alert pipeline.",
        icon="🚫",
    )
    st.info(
        "Memory Explorer, Consistency Audit, and Evaluation are still functional "
        "and use live Hindsight data.",
        icon="ℹ️",
    )


def render_command_center():
    render_html(
        f"""
        <div style="margin-bottom:1.3rem;">
            <div style="font-size:1.5rem; font-weight:700; color:{COLORS['text_primary']};">Command Center</div>
            <div style="font-size:0.85rem; color:{COLORS['text_secondary']};">
                Real-time overview of AML alert triage and institutional memory.
            </div>
        </div>
        """
    )

    if not using_dataset():
        _render_dataset_blocker()
        return

    st.success("Alert queue loaded from HI-Small dataset via alert generator.", icon="✅")

    all_alerts = get_alerts()
    high_risk = [a for a in all_alerts if a["risk"] == "HIGH"]
    reviewed = len(get_audit_trail())
    total_memories = sum(a.get("precedent_count", 0) for a in all_alerts)

    metric_row(
        [
            {"label": "Active Alerts", "value": str(len(all_alerts)), "accent": COLORS["accent"]},
            {"label": "High Risk", "value": str(len(high_risk)), "accent": COLORS["risk_high"]},
            {"label": "Reviewed", "value": str(reviewed), "accent": COLORS["risk_low"]},
            {"label": "Memories", "value": str(total_memories), "accent": COLORS["risk_medium"]},
        ]
    )

    st.write("")
    col_left, col_right = st.columns([2.2, 1])

    with col_left:
        st.markdown("**Priority Queue**")
        st.caption("Top alerts by risk — open the full queue in Alerts for search and filtering.")
        for alert in sorted(
            all_alerts,
            key=lambda a: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[a["risk"]]
        )[:3]:
            from ui.components.cards import alert_card

            def _go_to_alert(alert_id):
                st.session_state.active_view = "alerts"
                st.session_state.selected_alert = alert_id
                st.rerun()

            alert_card(alert, on_analyze=_go_to_alert)

        if st.button("View full alert queue →"):
            st.session_state.active_view = "alerts"
            st.rerun()

    with col_right:
        st.markdown("**How PRECEDENT works**")
        render_html(
            f"""
            <div style="background:{COLORS['surface']}; border:1px solid {COLORS['border']}; border-radius:10px; padding:1rem 1.1rem; font-size:0.78rem; color:{COLORS['text_secondary']}; line-height:2;">
                <div>1. AML alert triggers</div>
                <div>2. Retrieve customer memory</div>
                <div>3. Retrieve similar precedents</div>
                <div>4. Apply typology knowledge</div>
                <div>5. AI recommendation</div>
                <div>6. Analyst accepts or overrides</div>
                <div>7. Decision becomes future precedent</div>
            </div>
            """
        )
        render_html(
            f"""
            <div style="margin-top:0.8rem; background:{COLORS['accent_soft']}; border:1px solid {COLORS['accent_border']}; border-radius:10px; padding:0.9rem 1.1rem; font-size:0.76rem; color:{COLORS['text_secondary']};">
                PRECEDENT is a decision-support tool. The human analyst always makes the
                final call — the system never autonomously determines whether money
                laundering occurred.
            </div>
            """
        )


view = st.session_state.active_view

if view == "command_center":
    render_command_center()
elif view == "alerts":
    alerts_view.render()
elif view == "memory":
    memory_view.render()
elif view == "audit":
    audit_view.render()
elif view == "evaluation":
    evaluation_view.render()
else:
    render_command_center()