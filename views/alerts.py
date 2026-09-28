"""Alerts view: searchable queue + premium Case Intelligence experience."""

import streamlit as st

from data.live_alerts import get_alert, get_alerts
from data.mock_data import (
    get_pep_watchlist_status,
    get_typology_knowledge,
    get_audit_trail,
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
    # Clear any cached live analysis so re-opening re-runs fresh
    keys_to_clear = [k for k in st.session_state if k.startswith("live_analysis_")]
    for k in keys_to_clear:
        del st.session_state[k]
    st.rerun()


def _back_to_queue():
    st.session_state.selected_alert = None
    st.rerun()


# ============================================================
# INTEGRATION HELPERS
# ============================================================

def _build_alert_full(alert: dict) -> dict:
    """
    Merge the UI alert dict with additional fields the DecisionEngine needs.
    Fields come only from the existing alert dict — nothing is invented.

    For dataset-derived alerts, `transaction_pattern` is the comma-joined
    signal string from alert_generator (e.g. "rapid_movement, high_value_transaction").
    For mock alerts, it falls back to the typology label.
    """
    pep = get_pep_watchlist_status(alert.get("customer", ""))
    return {
        # Primary ID fields
        "alert_id": alert.get("alert_id") or alert.get("id", ""),
        "id":        alert.get("id") or alert.get("alert_id", ""),
        "customer_id": alert.get("customer_id", ""),
        # Typology/pattern fields — prefer genuine dataset values
        "typology": alert.get("typology", ""),
        "transaction_pattern": (
            alert.get("transaction_pattern")    # real signal string from dataset
            or alert.get("typology", "")        # mock-alert fallback
        ),
        "amount":   alert.get("amount", 0),
        "currency": alert.get("currency", "USD"),
        # Guardrail signals
        "pep_match":      pep.get("pep", False),
        "watchlist_match": pep.get("watchlist", False),
        # Preserve all original UI keys for UI rendering
        **alert,
    }



def _get_or_run_analysis(alert_full: dict) -> dict:
    """
    Run precedent_service.analyze_alert(alert_full) and cache the result.
    On failure, returns a result that clearly reports the error but does NOT
    substitute mock/fabricated precedents or decisions.
    """
    alert_id = alert_full.get("id", alert_full.get("alert_id", ""))
    cache_key = f"live_analysis_{alert_id}"

    if cache_key not in st.session_state:
        try:
            from integration.precedent_service import analyze_alert
            result = analyze_alert(alert_full)
        except Exception as exc:
            # Return a transparent error result — no mock data, no fabricated numbers.
            result = {
                "success":             False,
                "decision":            None,
                "recommendation":      None,
                "risk_level":          None,
                "confidence":          None,
                "confidence_raw":      None,
                "reason":              f"Analysis failed: {type(exc).__name__}: {exc}",
                "key_factors":         [],
                "precedents_used":     [],
                "precedent_count":     0,
                "memory_count":        0,
                "guardrail_applied":   False,
                "human_review_required": True,
                "latency_ms":          0,
                "error":               str(exc),
                "hindsight_precedents": [],
                "hindsight_available": False,
            }
        st.session_state[cache_key] = result

    return st.session_state[cache_key]



def _do_record_decision(
    alert_full: dict,
    agent_recommendation: str,
    final_decision: str,
    analyst_reason: str,
    analyst_note,
    confidence: int,
    precedents_used: list,
) -> dict:
    """
    Call integration.precedent_service.record_analyst_decision().
    Falls back to mock record_decision if integration is unavailable.
    Builds the entry dict the UI components expect.
    """
    from datetime import datetime

    try:
        from integration.precedent_service import record_analyst_decision
        result = record_analyst_decision(
            alert=alert_full,
            agent_recommendation=agent_recommendation,
            final_decision=final_decision,
            analyst_reason=analyst_reason,
            analyst_note=analyst_note,
            confidence=confidence,
            precedents_used=precedents_used,
        )
        override = result.get("override", False)
        entry = {
            "alert": alert_full.get("id", ""),
            "ai_recommendation": agent_recommendation,
            "confidence": confidence,
            "precedents_used": precedents_used,
            "human_decision": final_decision,
            "override": override,
            "override_reason": analyst_reason if override else None,
            "analyst_note": analyst_note,
            "timestamp": datetime.now().strftime("%d %b %Y, %H:%M"),
            "memory_update": result.get("memory_update", "Decision recorded."),
            "hindsight_success": result.get("success", False),
            "hindsight_error": result.get("error"),
        }
        return entry
    except Exception as exc:
        override = agent_recommendation.upper() != final_decision.upper()
        return {
            "alert": alert_full.get("id", ""),
            "ai_recommendation": agent_recommendation,
            "confidence": confidence,
            "precedents_used": precedents_used,
            "human_decision": final_decision,
            "override": override,
            "override_reason": analyst_reason if override else None,
            "analyst_note": analyst_note,
            "timestamp": datetime.now().strftime("%d %b %Y, %H:%M"),
            "memory_update": f"Memory update failed ({type(exc).__name__}) — decision logged locally only.",
            "hindsight_success": False,
            "hindsight_error": str(exc),
        }


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

    # --------------------------------------------------------
    # DATASET BLOCKER — must appear before any other content
    # --------------------------------------------------------
    from data.live_alerts import using_dataset as _using_dataset
    if not _using_dataset():
        render_html(
            f"""
            <div style="margin-bottom:1.35rem;">
                <div style="font-size:1.45rem;font-weight:750;
                            color:{COLORS['text_primary']};">Alert Queue</div>
            </div>
            """
        )
        st.error(
            "**FINAL BLOCKER — Dataset missing**\n\n"
            "`data/HI-Small/HI-Small_Trans.csv` is not present in this workspace.\n\n"
            "Place the file at that exact path and restart Streamlit. "
            "All integration code is ready — no further changes required.",
            icon="🚫",
        )
        st.info(
            "Memory Explorer, Consistency Audit, and Evaluation "
            "remain functional using live Hindsight data.",
            icon="ℹ️",
        )
        return

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

                # Run real analysis now (cached so reruns are instant)
                alert_full = _build_alert_full(alert)
                _get_or_run_analysis(alert_full)

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

    # Build the full alert dict the engine needs, then run real analysis
    alert_full = _build_alert_full(alert)
    decision = _get_or_run_analysis(alert_full)

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
        ) if decision.get("recommendation") is not None else st.error(
            f"Analysis failed: {decision.get('error', 'unknown error')}",
            icon="⚠️",
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
                        {len(decision.get('precedents_used', []))}
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

            if decision.get("recommendation") is None:
                # Analysis failed — cannot accept/override a non-existent recommendation
                st.warning(
                    "AI analysis did not produce a recommendation. "
                    f"Error: {decision.get('error', 'unknown')}. "
                    "Check Hindsight and Groq API connectivity.",
                    icon="⚠️",
                )
            else:
                action = review_actions(alert_id)

                if action == "accept":
                    entry = _do_record_decision(
                        alert_full,
                        decision["recommendation"],
                        decision["recommendation"],
                        "",
                        None,
                        decision["confidence"],
                        decision["precedents_used"],
                    )
                    decision_state[alert_id] = entry
                    st.rerun()

                elif action == "override":
                    st.session_state[f"show_override_{alert_id}"] = True

            if st.session_state.get(f"show_override_{alert_id}") and decision.get("recommendation"):

                st.markdown("")

                result = override_form(
                    alert_id,
                    decision["recommendation"],
                )

                if result:
                    human_decision, reason, note = result

                    entry = _do_record_decision(
                        alert_full,
                        decision["recommendation"],
                        human_decision,
                        reason,
                        note,
                        decision.get("confidence", 0),
                        decision.get("precedents_used", []),
                    )

                    decision_state[alert_id] = entry
                    st.session_state[f"show_override_{alert_id}"] = False
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

        # Use real Hindsight precedents from the live analysis result.
        # Fall back to mock precedents only if Hindsight is unavailable.
        hindsight_precedents = decision.get("hindsight_precedents", [])
        mock_fallback = decision.get("_mock_precedents", [])

        if hindsight_precedents:
            precedents = hindsight_precedents
            memory_source_label = "Hindsight"
        elif mock_fallback:
            precedents = mock_fallback
            memory_source_label = "Local (Hindsight unavailable)"
        else:
            precedents = []
            memory_source_label = "None"

        mem_count = decision.get("memory_count", len(precedents))
        hindsight_ok = decision.get("hindsight_available", True)

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
                    {len(precedents)} precedents · {mem_count} memories
                </div>

            </div>
            """
        )

        if not hindsight_ok and not hindsight_precedents:
            st.warning(
                "⚠ Hindsight is temporarily unavailable. "
                "Showing locally cached precedents."
                if mock_fallback
                else "⚠ Hindsight is temporarily unavailable. No precedents loaded."
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

            for i, precedent in enumerate(precedents):

                precedent_card(
                    precedent,
                    key_prefix=f"case_{alert_id}_{i}",
                )

        # ----------------------------------------------------
        # MEMORY SUMMARY
        # ----------------------------------------------------

        if precedents:

            clear_count = sum(
                1
                for p in precedents
                if p.get("decision", "") == "CLEAR"
            )

            escalate_count = sum(
                1
                for p in precedents
                if p.get("decision", "") == "ESCALATE"
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