"""Memory Explorer: Customer Memory, Precedent Cases, Typology Knowledge, Analyst Decisions."""

import streamlit as st

from data.mock_data import (
    CUSTOMERS,
    TYPOLOGIES,
    get_audit_trail,
)
from ui.components.precedent_card import precedent_card
from ui.styles.theme import COLORS, render_html


def render():
    render_html(
        f"""
        <div style="margin-bottom:1.2rem;">
            <div style="font-size:1.4rem;font-weight:800;
                        color:{COLORS['text_primary']};letter-spacing:0.01em;">
                Memory Explorer
            </div>
            <div style="font-size:0.78rem;color:{COLORS['text_secondary']};margin-top:3px;">
                Institutional memory — every analyst decision, precedent, and typology pattern.
            </div>
        </div>
        """
    )

    # ============================================================
    # MEMORY TABS
    # ============================================================

    tab_customer, tab_precedent, tab_typology, tab_decisions = st.tabs(
        [
            "Customer Memory",
            "Precedent Cases",
            "Typology Knowledge",
            "Analyst Decisions",
        ]
    )

    with tab_customer:
        _render_customer_memory()

    with tab_precedent:
        _render_precedent_cases()

    with tab_typology:
        _render_typology_knowledge()

    with tab_decisions:
        _render_analyst_decisions()


# ================================================================
# CUSTOMER MEMORY
# ================================================================

def _render_customer_memory():

    names = [c["name"] for c in CUSTOMERS.values()]

    selected = st.selectbox(
        "Select customer",
        names,
        key="memory_customer_select",
    )

    customer = next(
        c for c in CUSTOMERS.values()
        if c["name"] == selected
    )

    st.write("")

    # ------------------------------------------------------------
    # CUSTOMER PROFILE HERO
    # ------------------------------------------------------------

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
            padding:1.15rem 1.3rem;
            margin-bottom:1rem;
        ">

            <div style="
                display:flex;
                justify-content:space-between;
                align-items:flex-start;
                gap:20px;
                flex-wrap:wrap;
            ">

                <div>

                    <div style="
                        font-size:0.68rem;
                        color:{COLORS['text_muted']};
                        text-transform:uppercase;
                        letter-spacing:0.08em;
                    ">
                        Customer Memory
                    </div>

                    <div style="
                        font-size:1.25rem;
                        font-weight:750;
                        color:{COLORS['text_primary']};
                        margin-top:4px;
                    ">
                        {customer['name']}
                    </div>

                    <div style="
                        font-size:0.78rem;
                        color:{COLORS['text_secondary']};
                        margin-top:3px;
                    ">
                        {customer['id']} &nbsp;·&nbsp; {customer['segment']}
                    </div>

                </div>

                <div style="
                    text-align:right;
                    min-width:150px;
                ">

                    <div style="
                        font-size:0.65rem;
                        color:{COLORS['text_muted']};
                        text-transform:uppercase;
                        letter-spacing:0.07em;
                    ">
                        Onboarded
                    </div>

                    <div style="
                        font-size:0.82rem;
                        color:{COLORS['text_primary']};
                        margin-top:3px;
                    ">
                        {customer['onboarded']}
                    </div>

                </div>

            </div>

        </div>
        """
    )

    # ------------------------------------------------------------
    # SUMMARY METRICS
    # ------------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    metric_data = [
        (
            col1,
            "CLEARED CASES",
            customer["cleared_count"],
            COLORS["risk_low"],
        ),
        (
            col2,
            "ESCALATED CASES",
            customer["escalated_count"],
            COLORS["risk_medium"],
        ),
        (
            col3,
            "HISTORICAL ALERTS",
            len(customer["timeline"]),
            COLORS["accent"],
        ),
    ]

    for col, label, value, color in metric_data:

        with col:

            render_html(
                f"""
                <div style="
                    background:{COLORS['surface']};
                    border:1px solid {COLORS['border']};
                    border-top:2px solid {color};
                    border-radius:11px;
                    padding:0.95rem 1.05rem;
                ">

                    <div style="
                        font-size:0.67rem;
                        color:{COLORS['text_muted']};
                        text-transform:uppercase;
                        letter-spacing:0.06em;
                    ">
                        {label}
                    </div>

                    <div style="
                        font-size:1.45rem;
                        font-weight:750;
                        color:{COLORS['text_primary']};
                        margin-top:5px;
                    ">
                        {value}
                    </div>

                </div>
                """
            )

    st.write("")

    # ------------------------------------------------------------
    # CONSOLIDATED OBSERVATIONS
    # ------------------------------------------------------------

    st.markdown("**Consolidated observations**")

    for obs in customer["observations"]:

        render_html(
            f"""
            <div style="
                background:{COLORS['surface']};
                border:1px solid {COLORS['border']};
                border-left:3px solid {COLORS['accent']};
                border-radius:10px;
                padding:0.85rem 1rem;
                margin-bottom:0.55rem;
            ">

                <div style="
                    font-size:0.68rem;
                    color:{COLORS['accent']};
                    text-transform:uppercase;
                    letter-spacing:0.06em;
                    margin-bottom:5px;
                ">
                    Learned observation
                </div>

                <div style="
                    font-size:0.81rem;
                    color:{COLORS['text_primary']};
                    line-height:1.55;
                ">
                    "{obs}"
                </div>

            </div>
            """
        )

    st.write("")

    # ------------------------------------------------------------
    # PATTERNS + CONCERNS
    # ------------------------------------------------------------

    left, right = st.columns(2)

    with left:

        st.markdown("**Recurring patterns**")

        for pattern in customer["recurring_patterns"]:

            render_html(
                f"""
                <div style="
                    display:flex;
                    gap:9px;
                    align-items:flex-start;
                    padding:0.5rem 0;
                    border-bottom:1px solid {COLORS['border_soft']};
                ">

                    <span style="
                        width:6px;
                        height:6px;
                        border-radius:50%;
                        background:{COLORS['accent']};
                        margin-top:6px;
                        flex-shrink:0;
                    "></span>

                    <span style="
                        font-size:0.79rem;
                        color:{COLORS['text_secondary']};
                        line-height:1.45;
                    ">
                        {pattern}
                    </span>

                </div>
                """
            )

    with right:

        st.markdown("**Known concerns**")

        if customer["known_concerns"]:

            for concern in customer["known_concerns"]:

                render_html(
                    f"""
                    <div style="
                        display:flex;
                        gap:9px;
                        align-items:flex-start;
                        padding:0.5rem 0;
                        border-bottom:1px solid {COLORS['border_soft']};
                    ">

                        <span style="
                            width:6px;
                            height:6px;
                            border-radius:50%;
                            background:{COLORS['risk_medium']};
                            margin-top:6px;
                            flex-shrink:0;
                        "></span>

                        <span style="
                            font-size:0.79rem;
                            color:{COLORS['text_secondary']};
                            line-height:1.45;
                        ">
                            {concern}
                        </span>

                    </div>
                    """
                )

        else:

            render_html(
                f"""
                <div style="
                    background:{COLORS['surface']};
                    border:1px solid {COLORS['border']};
                    border-radius:9px;
                    padding:0.65rem 0.8rem;
                    color:{COLORS['text_muted']};
                    font-size:0.78rem;
                ">
                    No known concerns on record.
                </div>
                """
            )

    st.write("")
    st.markdown("**Decision timeline**")

    st.caption(
        "Historical analyst decisions associated with this customer."
    )

    # ------------------------------------------------------------
    # TIMELINE
    # ------------------------------------------------------------

    for index, event in enumerate(customer["timeline"]):

        decision = event["decision"]

        color = (
            COLORS["risk_low"]
            if decision == "CLEAR"
            else COLORS["risk_medium"]
        )

        render_html(
            f"""
            <div style="
                display:grid;
                grid-template-columns:110px 1fr 110px;
                align-items:center;
                gap:16px;
                padding:0.75rem 0.1rem;
                border-bottom:1px solid {COLORS['border_soft']};
            ">

                <div style="
                    font-size:0.74rem;
                    color:{COLORS['text_muted']};
                    white-space:nowrap;
                ">
                    {event['date']}
                </div>

                <div style="
                    display:flex;
                    align-items:center;
                    gap:10px;
                ">

                    <span style="
                        width:8px;
                        height:8px;
                        border-radius:50%;
                        background:{color};
                        box-shadow:0 0 8px {color}55;
                        flex-shrink:0;
                    "></span>

                    <span style="
                        font-size:0.82rem;
                        color:{COLORS['text_primary']};
                        font-weight:600;
                    ">
                        {event['alert']}
                    </span>

                </div>

                <div style="
                    text-align:right;
                    color:{color};
                    font-size:0.7rem;
                    font-weight:750;
                    letter-spacing:0.05em;
                ">
                    {decision}
                </div>

            </div>
            """
        )


# ================================================================
# PRECEDENT CASES
# ================================================================

def _render_precedent_cases():
    """Display precedent cases from live Hindsight memory bank."""

    st.caption("Historical precedents retrieved from Hindsight memory bank.")

    with st.spinner("Recalling precedents from Hindsight…"):
        try:
            from integration.precedent_service import _retrieve_and_filter_precedents
            # Use a broad synthetic query alert to recall all available precedents
            synthetic = {
                "alert_id": "MEMORY-EXPLORER",
                "id":       "MEMORY-EXPLORER",
                "typology": "AML",
                "transaction_pattern": "AML",
                "customer_id": "",
                "amount": 0,
            }
            recall = _retrieve_and_filter_precedents(synthetic)
            filtered = recall.get("filtered", [])
            hindsight_ok = recall.get("success", False)
        except Exception as exc:
            filtered = []
            hindsight_ok = False
            st.error(f"Hindsight recall error: {exc}")

    if not hindsight_ok:
        st.warning(
            "Hindsight memory bank is not reachable. "
            "Check HINDSIGHT_API_KEY and HINDSIGHT_BASE_URL in .env.",
            icon="⚠️",
        )
        return

    if not filtered:
        render_html(
            f"""
            <div style="background:{COLORS['surface']};border:1px solid {COLORS['border']};
                        border-radius:9px;padding:0.85rem 1rem;
                        color:{COLORS['text_muted']};font-size:0.8rem;">
                No authoritative precedents found in Hindsight bank.
                Decisions recorded during analyst review sessions will appear here.
            </div>
            """
        )
        return

    st.caption(f"{len(filtered)} historical precedent cases on record in Hindsight")

    for p in filtered:
        # Convert Hindsight precedent to the shape precedent_card expects
        card = {
            "id":         p.get("alert_id", "UNKNOWN"),
            "similarity": "Relevant precedent",
            "decision":   p.get("decision", "UNKNOWN"),
            "pattern":    p.get("typology", "Historical alert") or "Historical alert",
            "date":       p.get("timestamp", ""),
            "reason":     p.get("reason", ""),
            "analyst":    "Analyst",
            "matching_factors":  [f"Typology: {p['typology']}"] if p.get("typology") else ["Historical alert"],
            "differing_factors": ["Analyst overrode AI recommendation"] if p.get("override") else [],
            "memory_id":  p.get("memory_id", ""),
            "override":   p.get("override", False),
        }
        precedent_card(card, key_prefix="explorer")


# ================================================================
# TYPOLOGY KNOWLEDGE
# ================================================================

def _render_typology_knowledge():

    for name, info in TYPOLOGIES.items():

        with st.expander(name):

            render_html(
                f"""
                <div style="
                    color:{COLORS['text_primary']};
                    font-size:0.82rem;
                    line-height:1.55;
                    margin-bottom:0.8rem;
                ">
                    {info['description']}
                </div>
                """
            )

            st.markdown("**Indicators**")

            for indicator in info["indicators"]:

                st.write(
                    f"• {indicator}"
                )

            st.markdown("**Guardrails**")

            for guardrail in info["guardrails"]:

                st.write(
                    f"• {guardrail}"
                )


# ================================================================
# ANALYST DECISIONS
# ================================================================

def _render_analyst_decisions():

    trail = get_audit_trail()

    if not trail:

        st.caption(
            "No analyst decisions recorded yet this session."
        )

        return

    for entry in trail:

        is_override = entry["override"]

        color = (
            COLORS["risk_medium"]
            if is_override
            else COLORS["risk_low"]
        )

        badge = (
            "OVERRIDE"
            if is_override
            else "ACCEPTED"
        )

        render_html(
            f"""
            <div style="
                background:{COLORS['surface']};
                border:1px solid {COLORS['border']};
                border-left:3px solid {color};
                border-radius:10px;
                padding:0.95rem 1.1rem;
                margin-bottom:0.6rem;
            ">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    gap:10px;
                    flex-wrap:wrap;
                ">

                    <span style="
                        font-weight:700;
                        color:{COLORS['text_primary']};
                        font-size:0.85rem;
                    ">
                        {entry['alert']}
                    </span>

                    <span style="
                        color:{color};
                        font-size:0.68rem;
                        font-weight:750;
                        letter-spacing:0.06em;
                    ">
                        {badge}
                    </span>

                </div>

                <div style="
                    color:{COLORS['text_secondary']};
                    font-size:0.78rem;
                    margin-top:6px;
                ">
                    AI: {entry['ai_recommendation']}
                    ({entry['confidence']}%)
                    <span style="color:{COLORS['text_muted']};">
                        →
                    </span>
                    Human: {entry['human_decision']}
                </div>

                <div style="
                    display:flex;
                    justify-content:space-between;
                    gap:12px;
                    flex-wrap:wrap;
                    margin-top:6px;
                ">

                    <span style="
                        color:{COLORS['text_muted']};
                        font-size:0.7rem;
                    ">
                        {entry['timestamp']}
                    </span>

                    <span style="
                        color:{COLORS['text_muted']};
                        font-size:0.7rem;
                    ">
                        {len(entry['precedents_used'])} precedent(s) used
                    </span>

                </div>

                {
                    f'''
                    <div style="
                        margin-top:8px;
                        padding-top:8px;
                        border-top:1px solid {COLORS["border_soft"]};
                        font-size:0.73rem;
                        color:{COLORS["text_secondary"]};
                    ">
                        <span style="color:{color}; font-weight:600;">
                            Memory update:
                        </span>
                        &nbsp;{entry["memory_update"]}
                    </div>
                    '''
                    if entry.get("memory_update")
                    else ""
                }

            </div>
            """
        )