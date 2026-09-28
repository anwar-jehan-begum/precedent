"""Alerts view: searchable queue + premium Case Intelligence experience."""

import streamlit as st

from data.mock_data import (
    get_alert,
    get_alerts,
    get_pep_watchlist_status,
    get_precedents,
    get_typology_knowledge,
    generate_decision,
    record_decision,
)
from ui.components.cards import alert_card
from ui.components.decision_card import (
    decision_confirmation,
    override_form,
    recommendation_card,
    review_actions,
)
from ui.components.precedent_card import precedent_card
from ui.components.trace import run_memory_trace
from ui.styles.theme import COLORS, render_html, risk_color


# ============================================================
# STATE HELPERS
# ============================================================

def _ensure_case_state():
    if "selected_alert" not in st.session_state:
        st.session_state.selected_alert = None

    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = {}

    if "decision_recorded" not in st.session_state:
        st.session_state.decision_recorded = {}


def _select_alert(alert_id: str):
    st.session_state.selected_alert = alert_id
    st.session_state.analysis_complete = {}
    st.session_state.decision_recorded = {}
    st.session_state[f"show_override_{alert_id}"] = False
    st.rerun()


def _back_to_queue():
    st.session_state.selected_alert = None
    st.rerun()


# ============================================================
# MAIN ENTRY
# ============================================================

def render():
    _ensure_case_state()

    if st.session_state.get("selected_alert"):
        _render_case_intelligence(
            st.session_state.selected_alert
        )
    else:
        _render_queue()


# ============================================================
# ALERT QUEUE
# ============================================================

def _render_queue():

    render_html(
        f"""
        <div style="
            margin-bottom:1.35rem;
        ">

            <div style="
                font-size:1.45rem;
                font-weight:750;
                color:{COLORS['text_primary']};
            ">
                Alert Queue
            </div>

            <div style="
                font-size:0.82rem;
                color:{COLORS['text_secondary']};
                margin-top:4px;
            ">
                Open AML alerts awaiting analyst review,
                ranked by risk.
            </div>

        </div>
        """
    )

    # --------------------------------------------------------
    # SEARCH / FILTER
    # --------------------------------------------------------

    col_search, col_filter = st.columns([3, 1])

    with col_search:

        query = st.text_input(
            "Search by alert ID or customer",
            placeholder="Search AML-1068, Meridian Imports...",
            label_visibility="collapsed",
        )

    with col_filter:

        risk_filter = st.selectbox(
            "Risk",
            ["All", "HIGH", "MEDIUM", "LOW"],
            label_visibility="collapsed",
        )

    alerts = get_alerts()

    if query:

        q = query.lower()

        alerts = [
            alert
            for alert in alerts
            if (
                q in alert["id"].lower()
                or q in alert["customer"].lower()
                or q in alert["typology"].lower()
            )
        ]

    if risk_filter != "All":

        alerts = [
            alert
            for alert in alerts
            if alert["risk"] == risk_filter
        ]

    st.write("")

    # --------------------------------------------------------
    # QUEUE SUMMARY
    # --------------------------------------------------------

    high = sum(
        1 for alert in alerts
        if alert["risk"] == "HIGH"
    )

    medium = sum(
        1 for alert in alerts
        if alert["risk"] == "MEDIUM"
    )

    low = sum(
        1 for alert in alerts
        if alert["risk"] == "LOW"
    )

    render_html(
        f"""
        <div style="
            display:flex;
            gap:10px;
            flex-wrap:wrap;
            margin-bottom:1rem;
        ">

            <span style="
                padding:5px 10px;
                border-radius:999px;
                background:{COLORS['surface']};
                border:1px solid {COLORS['border']};
                color:{COLORS['text_secondary']};
                font-size:0.7rem;
            ">
                {len(alerts)} active
            </span>

            <span style="
                padding:5px 10px;
                border-radius:999px;
                background:{COLORS['risk_high_soft']};
                border:1px solid {COLORS['risk_high']}55;
                color:{COLORS['risk_high']};
                font-size:0.7rem;
                font-weight:650;
            ">
                {high} high
            </span>

            <span style="
                padding:5px 10px;
                border-radius:999px;
                background:{COLORS['risk_medium_soft']};
                border:1px solid {COLORS['risk_medium']}55;
                color:{COLORS['risk_medium']};
                font-size:0.7rem;
                font-weight:650;
            ">
                {medium} medium
            </span>

            <span style="
                padding:5px 10px;
                border-radius:999px;
                background:{COLORS['risk_low_soft']};
                border:1px solid {COLORS['risk_low']}55;
                color:{COLORS['risk_low']};
                font-size:0.7rem;
                font-weight:650;
            ">
                {low} low
            </span>

        </div>
        """
    )

    if not alerts:

        st.info(
            "No alerts match your search."
        )

        return

    # --------------------------------------------------------
    # ALERT CARDS
    # --------------------------------------------------------

    for alert in alerts:

        alert_card(
            alert,
            on_analyze=_select_alert,
        )


# ============================================================
# CASE INTELLIGENCE
# ============================================================

def _render_case_intelligence(alert_id: str):

    alert = get_alert(alert_id)

    if not alert:

        st.error(
            "Alert not found."
        )

        return

    risk = alert["risk"]
    risk_colour = risk_color(risk)

    analysis_state = st.session_state.analysis_complete
    decision_state = st.session_state.decision_recorded

    is_analyzed = analysis_state.get(
        alert_id,
        False
    )

    saved_decision = decision_state.get(
        alert_id
    )

    # ========================================================
    # TOP HEADER
    # ========================================================

    top_left, top_right = st.columns(
        [5, 1]
    )

    with top_left:

        render_html(
            f"""
            <div style="
                margin-bottom:0.2rem;
            ">

                <div style="
                    font-size:0.67rem;
                    color:{COLORS['text_muted']};
                    text-transform:uppercase;
                    letter-spacing:0.09em;
                ">
                    Case Intelligence
                </div>

                <div style="
                    display:flex;
                    align-items:center;
                    gap:12px;
                    flex-wrap:wrap;
                    margin-top:5px;
                ">

                    <span style="
                        font-size:1.55rem;
                        font-weight:800;
                        color:{COLORS['text_primary']};
                    ">
                        {alert['id']}
                    </span>

                    <span style="
                        font-size:1.08rem;
                        color:{COLORS['text_secondary']};
                    ">
                        {alert['customer']}
                    </span>

                    <span style="
                        color:{COLORS['text_secondary']};
                        font-size:1.0rem;
                    ">
                        ₹{alert['amount']:,}
                    </span>

                    <span style="
                        background:{risk_colour}18;
                        color:{risk_colour};
                        border:1px solid {risk_colour}55;
                        border-radius:6px;
                        padding:3px 9px;
                        font-size:0.69rem;
                        font-weight:750;
                        letter-spacing:0.05em;
                    ">
                        {risk} RISK
                    </span>

                    <span style="
                        color:{COLORS['text_muted']};
                        font-size:0.8rem;
                    ">
                        {alert['typology']}
                    </span>

                </div>

            </div>
            """
        )

    with top_right:

        if st.button(
            "← Back to Queue",
            use_container_width=True,
            key=f"back_{alert_id}",
        ):

            _back_to_queue()

    st.markdown("<br>", unsafe_allow_html=True)

    # ========================================================
    # PRE-ANALYSIS STATE
    # ========================================================

    if not is_analyzed:

        render_html(
            f"""
            <div style="
                background:
                    linear-gradient(
                        135deg,
                        {COLORS['surface_alt']},
                        {COLORS['surface']}
                    );
                border:1px solid {COLORS['border']};
                border-radius:14px;
                padding:1.25rem;
                margin-bottom:1rem;
            ">

                <div style="
                    font-size:0.68rem;
                    color:{COLORS['accent']};
                    text-transform:uppercase;
                    letter-spacing:0.08em;
                    font-weight:700;
                ">
                    Ready for investigation
                </div>

                <div style="
                    font-size:1.05rem;
                    font-weight:700;
                    color:{COLORS['text_primary']};
                    margin-top:5px;
                ">
                    Retrieve this case's institutional memory
                </div>

                <div style="
                    color:{COLORS['text_secondary']};
                    font-size:0.8rem;
                    line-height:1.55;
                    margin-top:5px;
                    max-width:760px;
                ">
                    PRECEDENT will inspect customer history,
                    search historical precedents, apply typology
                    knowledge, and prepare an analyst recommendation.
                </div>

            </div>
            """
        )

        analyze_col, space_col = st.columns(
            [1, 4]
        )

        with analyze_col:

            if st.button(
                "▶ Analyze Case",
                key=f"run_analyze_{alert_id}",
                type="primary",
                use_container_width=True,
            ):

                trace_placeholder = st.empty()

                run_memory_trace(
                    trace_placeholder,
                    delay=0.4,
                )

                trace_placeholder.empty()

                analysis_state[alert_id] = True

                st.rerun()

        with space_col:

            st.caption(
                "Human review remains required for the final decision."
            )

        return

    # ========================================================
    # ANALYSIS COMPLETE — THREE-PANEL LAYOUT
    # ========================================================

    left, center, right = st.columns(
        [1.08, 1.25, 1.38]
    )

    # ========================================================
    # LEFT — CURRENT ALERT
    # ========================================================

    with left:

        render_html(
            f"""
            <div style="
                font-size:0.72rem;
                font-weight:700;
                color:{COLORS['text_primary']};
                margin-bottom:8px;
            ">
                Current Alert
                <span style="
                    color:{COLORS['text_muted']};
                    font-weight:400;
                ">
                    · Risk Signals
                </span>
            </div>
            """
        )

        pep = get_pep_watchlist_status(
            alert["customer"]
        )

        has_guardrail = (
            pep["pep"]
            or pep["watchlist"]
        )

        if has_guardrail:

            pep_line = "PEP / watchlist match detected"
            guardrail_colour = COLORS["risk_high"]

        else:

            pep_line = "No PEP / watchlist match"
            guardrail_colour = COLORS["risk_low"]

        render_html(
            f"""
            <div style="
                background:{COLORS['surface']};
                border:1px solid {COLORS['border']};
                border-radius:12px;
                padding:1rem 1.05rem;
            ">

                <div style="
                    display:grid;
                    grid-template-columns:1fr 1fr;
                    gap:12px;
                    margin-bottom:12px;
                ">

                    <div>
                        <div style="
                            color:{COLORS['text_muted']};
                            font-size:0.64rem;
                            text-transform:uppercase;
                        ">
                            Amount
                        </div>

                        <div style="
                            color:{COLORS['text_primary']};
                            font-size:0.86rem;
                            font-weight:650;
                            margin-top:3px;
                        ">
                            ₹{alert['amount']:,}
                        </div>
                    </div>

                    <div>
                        <div style="
                            color:{COLORS['text_muted']};
                            font-size:0.64rem;
                            text-transform:uppercase;
                        ">
                            Typology
                        </div>

                        <div style="
                            color:{COLORS['text_primary']};
                            font-size:0.86rem;
                            font-weight:650;
                            margin-top:3px;
                        ">
                            {alert['typology']}
                        </div>
                    </div>

                </div>

                <div style="
                    color:{COLORS['text_muted']};
                    font-size:0.65rem;
                    text-transform:uppercase;
                    letter-spacing:0.04em;
                ">
                    Geography
                </div>

                <div style="
                    color:{COLORS['text_primary']};
                    font-size:0.78rem;
                    margin-top:4px;
                    line-height:1.45;
                ">
                    {", ".join(alert['geography'])}
                </div>

                <div style="
                    margin-top:14px;
                    padding-top:11px;
                    border-top:1px solid {COLORS['border_soft']};
                ">

                    <div style="
                        color:{COLORS['text_muted']};
                        font-size:0.65rem;
                        text-transform:uppercase;
                        letter-spacing:0.04em;
                        margin-bottom:5px;
                    ">
                        Risk indicators
                    </div>

                    <ul style="
                        margin:0 0 0 17px;
                        padding:0;
                        color:{COLORS['text_primary']};
                        font-size:0.77rem;
                        line-height:1.55;
                    ">
                        {
                            ''.join(
                                f"<li>{signal}</li>"
                                for signal in alert["signals"]
                            )
                        }
                    </ul>

                </div>

                <div style="
                    margin-top:12px;
                    padding-top:10px;
                    border-top:1px solid {COLORS['border_soft']};
                    color:{guardrail_colour};
                    font-size:0.72rem;
                    font-weight:600;
                ">
                    ● {pep_line}
                </div>

            </div>
            """
        )

        typology = get_typology_knowledge(
            alert["typology"]
        )

        if typology:

            with st.expander(
                "Typology knowledge"
            ):

                st.markdown(
                    typology["description"]
                )

                st.markdown(
                    "**Key indicators**"
                )

                for indicator in typology["indicators"]:

                    st.write(
                        f"• {indicator}"
                    )

                st.markdown(
                    "**Guardrails**"
                )

                for guardrail in typology["guardrails"]:

                    st.write(
                        f"• {guardrail}"
                    )

    # ========================================================
    # CENTER — AI DECISION
    # ========================================================

    decision = generate_decision(
        alert
    )

    with center:

        render_html(
            f"""
            <div style="
                font-size:0.72rem;
                font-weight:700;
                color:{COLORS['text_primary']};
                margin-bottom:8px;
            ">
                AI Recommendation
                <span style="
                    color:{COLORS['risk_low']};
                    font-size:0.62rem;
                    margin-left:6px;
                ">
                    ● MEMORY ENABLED
                </span>
            </div>
            """
        )

        recommendation_card(
            decision
        )

        st.write("")

        with st.expander(
            "View reasoning",
            expanded=False,
        ):

            render_html(
                f"""
                <div style="
                    padding:0.15rem 0;
                    font-size:0.79rem;
                    line-height:1.6;
                    color:{COLORS['text_secondary']};
                ">

                    <div style="
                        color:{COLORS['text_muted']};
                        font-size:0.65rem;
                        text-transform:uppercase;
                        letter-spacing:0.06em;
                        margin-bottom:5px;
                    ">
                        Decision context
                    </div>

                    PRECEDENT retrieved
                    <b style="color:{COLORS['text_primary']};">
                        {len(decision['precedents_used'])}
                    </b>
                    historical precedent(s) and evaluated the
                    customer's memory profile before generating
                    the recommendation.

                </div>
                """
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ----------------------------------------------------
        # ANALYST REVIEW
        # ----------------------------------------------------

        render_html(
            f"""
            <div style="
                font-size:0.72rem;
                font-weight:700;
                color:{COLORS['text_primary']};
                margin-bottom:8px;
            ">
                Analyst Review
            </div>
            """
        )

        if not saved_decision:

            action = review_actions(
                alert_id
            )

            if action == "accept":

                entry = record_decision(
                    alert_id,
                    decision["recommendation"],
                    decision["recommendation"],
                    None,
                    None,
                    decision["confidence"],
                    decision["precedents_used"],
                )

                decision_state[alert_id] = entry

                st.rerun()

            elif action == "override":

                st.session_state[
                    f"show_override_{alert_id}"
                ] = True

            if st.session_state.get(
                f"show_override_{alert_id}"
            ):

                st.markdown("")

                result = override_form(
                    alert_id,
                    decision["recommendation"],
                )

                if result:

                    (
                        human_decision,
                        reason,
                        note,
                    ) = result

                    entry = record_decision(
                        alert_id,
                        decision["recommendation"],
                        human_decision,
                        reason,
                        note,
                        decision["confidence"],
                        decision["precedents_used"],
                    )

                    decision_state[alert_id] = entry

                    st.session_state[
                        f"show_override_{alert_id}"
                    ] = False

                    st.rerun()

        else:

            decision_confirmation(
                saved_decision
            )

            # ------------------------------------------------
            # LEARNING STATE
            # ------------------------------------------------

            render_html(
                f"""
                <div style="
                    margin-top:10px;
                    background:
                        linear-gradient(
                            135deg,
                            {COLORS['accent_soft']},
                            {COLORS['surface']}
                        );
                    border:1px solid {COLORS['accent_border']};
                    border-radius:10px;
                    padding:0.85rem 1rem;
                ">

                    <div style="
                        color:{COLORS['accent']};
                        font-size:0.67rem;
                        font-weight:750;
                        letter-spacing:0.07em;
                        text-transform:uppercase;
                    ">
                        Precedent learned
                    </div>

                    <div style="
                        color:{COLORS['text_secondary']};
                        font-size:0.76rem;
                        margin-top:4px;
                        line-height:1.5;
                    ">
                        The analyst decision has been recorded as
                        organizational knowledge for future similar alerts.
                    </div>

                </div>
                """
            )

    # ========================================================
    # RIGHT — MEMORY INFLUENCE
    # ========================================================

    with right:

        precedents = get_precedents(
            alert_id
        )

        render_html(
            f"""
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                gap:10px;
                margin-bottom:8px;
            ">

                <div style="
                    font-size:0.72rem;
                    font-weight:700;
                    color:{COLORS['text_primary']};
                ">
                    Memory Influence
                </div>

                <div style="
                    font-size:0.66rem;
                    color:{COLORS['accent']};
                    background:{COLORS['accent_soft']};
                    border:1px solid {COLORS['accent_border']};
                    border-radius:999px;
                    padding:3px 8px;
                ">
                    {len(precedents)} precedents
                </div>

            </div>
            """
        )

        if not precedents:

            st.caption(
                "No historical precedents retrieved for this alert."
            )

        else:

            render_html(
                f"""
                <div style="
                    color:{COLORS['text_muted']};
                    font-size:0.7rem;
                    line-height:1.4;
                    margin-bottom:8px;
                ">
                    Historical analyst decisions surfaced
                    because their transaction patterns resemble
                    the current alert.
                </div>
                """
            )

            for precedent in precedents:

                precedent_card(
                    precedent,
                    key_prefix=f"case_{alert_id}",
                )

        # ----------------------------------------------------
        # MEMORY SUMMARY
        # ----------------------------------------------------

        if precedents:

            clear_count = sum(
                1
                for p in precedents
                if p["decision"] == "CLEAR"
            )

            escalate_count = sum(
                1
                for p in precedents
                if p["decision"] == "ESCALATE"
            )

            render_html(
                f"""
                <div style="
                    margin-top:0.7rem;
                    background:{COLORS['surface']};
                    border:1px solid {COLORS['border']};
                    border-radius:10px;
                    padding:0.75rem 0.9rem;
                ">

                    <div style="
                        color:{COLORS['text_muted']};
                        font-size:0.64rem;
                        text-transform:uppercase;
                        letter-spacing:0.05em;
                    ">
                        Retrieved decision pattern
                    </div>

                    <div style="
                        display:flex;
                        gap:18px;
                        margin-top:8px;
                    ">

                        <span style="
                            color:{COLORS['risk_low']};
                            font-size:0.74rem;
                            font-weight:650;
                        ">
                            ● {clear_count} CLEAR
                        </span>

                        <span style="
                            color:{COLORS['risk_medium']};
                            font-size:0.74rem;
                            font-weight:650;
                        ">
                            ● {escalate_count} ESCALATE
                        </span>

                    </div>

                </div>
                """
            )