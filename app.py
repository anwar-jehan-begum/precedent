"""
PRECEDENT — AML Decision Intelligence
Enterprise-grade, hackathon-ready frontend.

Run:  streamlit run app.py
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


# ---------------------------------------------------------------------------
# Dataset blocker (shown when HI-Small CSV absent)
# ---------------------------------------------------------------------------

def _render_dataset_blocker():
    render_html(
        f"""
        <div style="
            background:{COLORS['surface']};
            border:1px solid #EF444430;
            border-left:3px solid #EF4444;
            border-radius:10px;
            padding:1.2rem 1.4rem;
            margin-bottom:1rem;
        ">
            <div style="
                font-size:0.65rem;font-weight:700;letter-spacing:0.1em;
                color:#EF4444;text-transform:uppercase;margin-bottom:6px;
            ">Dataset Missing</div>
            <div style="font-size:0.88rem;font-weight:600;color:{COLORS['text_primary']};
                        margin-bottom:4px;">
                HI-Small dataset not found at
                <code style="background:{COLORS['surface_alt']};padding:1px 5px;border-radius:4px;
                             font-size:0.8rem;">data/HI-Small/HI-Small_Trans.csv</code>
            </div>
            <div style="font-size:0.78rem;color:{COLORS['text_secondary']};line-height:1.6;">
                Place the file at that path and restart Streamlit.
                All code is ready — no other change needed to activate the real alert pipeline.<br>
                Memory Explorer, Consistency Audit, and Evaluation remain fully functional
                using live Hindsight data.
            </div>
        </div>
        """
    )


# ---------------------------------------------------------------------------
# Visual system workflow diagram
# ---------------------------------------------------------------------------

def _render_workflow():
    nodes = [
        ("AML Alert",         COLORS["risk_high"],   "Transaction monitoring flag"),
        ("Customer Memory",   COLORS["accent"],      "Hindsight recall"),
        ("Precedents",        COLORS["accent"],      "Historical decisions"),
        ("AI Recommendation", COLORS["risk_medium"], "Groq LLM + guardrails"),
        ("Analyst Decision",  COLORS["risk_low"],    "Accept / Override"),
        ("New Precedent",     COLORS["risk_low"],    "Retained in Hindsight"),
    ]

    arrows_html = ""
    nodes_html = ""
    for i, (label, color, sub) in enumerate(nodes):
        nodes_html += f"""
        <div style="
            display:flex;flex-direction:column;align-items:center;
            min-width:100px;flex:1;
        ">
            <div style="
                background:{COLORS['surface_alt']};
                border:1px solid {color}44;
                border-top:2px solid {color};
                border-radius:8px;
                padding:0.55rem 0.6rem;
                text-align:center;
                width:100%;
            ">
                <div style="font-size:0.7rem;font-weight:700;color:{color};
                            letter-spacing:0.02em;">{label}</div>
                <div style="font-size:0.6rem;color:{COLORS['text_muted']};
                            margin-top:2px;">{sub}</div>
            </div>
            {"<div style='font-size:0.8rem;color:" + COLORS['text_faint'] + ";margin:0 2px;align-self:center;'>→</div>" if i < len(nodes)-1 else ""}
        </div>
        """

    render_html(
        f"""
        <div style="margin-bottom:0.5rem;">
            <div style="font-size:0.63rem;font-weight:700;letter-spacing:0.09em;
                        color:{COLORS['text_muted']};text-transform:uppercase;
                        margin-bottom:0.6rem;">Investigation Flow</div>
            <div style="display:flex;align-items:stretch;gap:0;
                        overflow-x:auto;padding-bottom:4px;">
                {nodes_html}
            </div>
            <div style="margin-top:8px;font-size:0.68rem;color:{COLORS['text_muted']};
                        border-top:1px solid {COLORS['border_soft']};padding-top:6px;">
                PRECEDENT is a decision-support tool.
                The human analyst always makes the final call.
            </div>
        </div>
        """
    )


# ---------------------------------------------------------------------------
# Command Center
# ---------------------------------------------------------------------------

def render_command_center():

    # Page header
    ds_ok = using_dataset()
    status_col = COLORS["risk_low"] if ds_ok else COLORS["risk_medium"]
    status_txt = "DATASET ACTIVE" if ds_ok else "DEMO MODE — dataset missing"
    dot = f'<span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:{status_col};box-shadow:0 0 5px {status_col}80;"></span>'

    render_html(
        f"""
        <div style="margin-bottom:1.2rem;">
            <div style="
                display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;
                margin-bottom:4px;
            ">
                <div style="font-size:1.4rem;font-weight:800;
                            color:{COLORS['text_primary']};letter-spacing:0.01em;">
                    Command Center
                </div>
                <div style="
                    display:inline-flex;align-items:center;gap:5px;
                    background:{COLORS['surface_alt']};
                    border:1px solid {COLORS['border']};
                    border-radius:999px;
                    padding:3px 10px;
                    font-size:0.62rem;font-weight:700;
                    color:{status_col};letter-spacing:0.07em;
                ">
                    {dot} {status_txt}
                </div>
            </div>
            <div style="font-size:0.8rem;color:{COLORS['text_secondary']};">
                Real-time overview of AML alert triage and institutional memory.
                The analyst workbench for the PRECEDENT decision pipeline.
            </div>
        </div>
        """
    )

    if not ds_ok:
        _render_dataset_blocker()
        return

    all_alerts = get_alerts()
    high_risk  = [a for a in all_alerts if a["risk"] == "HIGH"]
    med_risk   = [a for a in all_alerts if a["risk"] == "MEDIUM"]
    reviewed   = len(get_audit_trail())

    # KPI row
    metric_row([
        {
            "label": "Active Alerts",
            "value": str(len(all_alerts)),
            "sublabel": "From HI-Small dataset",
            "accent": COLORS["accent"],
            "icon": "⚑",
        },
        {
            "label": "High Risk",
            "value": str(len(high_risk)),
            "sublabel": f"{len(med_risk)} medium risk",
            "accent": COLORS["risk_high"],
            "icon": "▲",
        },
        {
            "label": "Reviewed",
            "value": str(reviewed),
            "sublabel": "Analyst decisions this session",
            "accent": COLORS["risk_low"],
            "icon": "✓",
        },
        {
            "label": "Alert Queue",
            "value": f"{len(all_alerts) - reviewed}",
            "sublabel": "Awaiting analyst review",
            "accent": COLORS["risk_medium"],
            "icon": "◈",
        },
    ])

    st.write("")

    col_queue, col_right = st.columns([2.3, 1])

    with col_queue:
        render_html(
            f"""
            <div style="margin-bottom:0.6rem;display:flex;
                        align-items:center;justify-content:space-between;">
                <div>
                    <div style="font-size:0.8rem;font-weight:700;
                                color:{COLORS['text_primary']};">Priority Queue</div>
                    <div style="font-size:0.7rem;color:{COLORS['text_muted']};margin-top:1px;">
                        Top alerts by risk — sorted HIGH → MEDIUM → LOW
                    </div>
                </div>
            </div>
            """
        )
        for alert in sorted(
            all_alerts,
            key=lambda a: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[a["risk"]],
        )[:4]:
            from ui.components.cards import alert_card

            def _go(aid):
                st.session_state.active_view = "alerts"
                st.session_state.selected_alert = aid
                st.rerun()

            alert_card(alert, on_analyze=_go)

        if st.button("Open full alert queue  →", type="secondary"):
            st.session_state.active_view = "alerts"
            st.rerun()

    with col_right:
        _render_workflow()

        st.write("")

        # System status panel
        from memory.health import check_hindsight_configuration
        try:
            health = check_hindsight_configuration()
            hs_ok   = health["ok"]
            hs_lat  = health.get("latency_ms", 0)
            hs_col  = COLORS["risk_low"] if hs_ok else COLORS["risk_medium"]
            hs_txt  = f"Connected · {hs_lat}ms" if hs_ok else "Unavailable"
            hs_dot  = f'<span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:{hs_col};"></span>'
        except Exception:
            hs_col, hs_txt, hs_dot = COLORS["risk_medium"], "Unavailable", ""

        render_html(
            f"""
            <div style="
                background:{COLORS['surface']};
                border:1px solid {COLORS['border']};
                border-radius:9px;
                padding:0.8rem 1rem;
            ">
                <div style="font-size:0.63rem;font-weight:700;letter-spacing:0.09em;
                            color:{COLORS['text_muted']};text-transform:uppercase;
                            margin-bottom:8px;">System Status</div>
                <div style="display:flex;flex-direction:column;gap:6px;font-size:0.75rem;">
                    <div style="display:flex;justify-content:space-between;
                                color:{COLORS['text_secondary']};">
                        <span>Alert Pipeline</span>
                        <span style="color:{COLORS['risk_low']};font-weight:600;">
                            ● ACTIVE
                        </span>
                    </div>
                    <div style="display:flex;justify-content:space-between;
                                color:{COLORS['text_secondary']};">
                        <span>Hindsight Memory</span>
                        <span style="color:{hs_col};font-weight:600;">
                            {hs_dot} {hs_txt}
                        </span>
                    </div>
                    <div style="display:flex;justify-content:space-between;
                                color:{COLORS['text_secondary']};">
                        <span>DecisionEngine</span>
                        <span style="color:{COLORS['risk_low']};font-weight:600;">
                            ● Groq LLM
                        </span>
                    </div>
                </div>
            </div>
            """
        )


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

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