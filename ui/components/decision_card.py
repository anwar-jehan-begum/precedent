"""AI recommendation card + analyst accept/override workflow."""

import streamlit as st

from ui.styles.theme import COLORS, render_html, risk_color


def recommendation_card(decision: dict):
    rec = decision["recommendation"]
    color = COLORS["risk_medium"] if rec == "ESCALATE" else COLORS["risk_low"]

    render_html(
        f"""
        <div style="
            background:{COLORS['surface']};
            border:1px solid {COLORS['border']};
            border-top: 2px solid {color};
            border-radius:12px;
            padding: 1.3rem 1.4rem;
        ">
            <div style="font-size:0.7rem; color:{COLORS['text_muted']}; letter-spacing:0.06em; text-transform:uppercase;">
                PRECEDENT Recommends
            </div>
            <div style="font-size:1.6rem; font-weight:800; color:{color}; margin-top:6px;">
                {rec}
            </div>
            <div style="font-size:0.78rem; color:{COLORS['text_secondary']}; margin-top:2px;">
                {decision['confidence']}% confidence
            </div>
            <div style="margin-top:0.9rem; font-size:0.82rem; color:{COLORS['text_primary']}; line-height:1.55; font-style:italic;">
                "{decision['reason']}"
            </div>
        </div>
        """
    )


def review_actions(alert_id: str):
    """
    Renders Accept / Override buttons. Returns one of:
    None, "accept", "override"
    """
    col1, col2 = st.columns(2)
    action = None

    with col1:
        if st.button(
            "Accept Recommendation",
            key=f"accept_{alert_id}",
            use_container_width=True,
            type="primary"
        ):
            action = "accept"

    with col2:
        if st.button(
            "Override Decision",
            key=f"override_{alert_id}",
            use_container_width=True
        ):
            action = "override"

    return action


def override_form(alert_id: str, ai_recommendation: str):
    """
    Renders the override drawer.
    Returns (human_decision, reason, note) or None if not yet submitted.
    """

    with st.form(key=f"override_form_{alert_id}"):

        st.markdown(
            f"**Override AI recommendation ({ai_recommendation})**"
        )

        human_decision = st.selectbox(
            "Human decision",
            options=["CLEAR", "ESCALATE"],
            index=1 if ai_recommendation == "CLEAR" else 0,
            key=f"human_decision_{alert_id}",
        )

        reason = st.text_area(
            "Override reason",
            key=f"reason_{alert_id}",
            height=80
        )

        note = st.text_area(
            "Analyst note (optional)",
            key=f"note_{alert_id}",
            height=60
        )

        submitted = st.form_submit_button(
            "Submit Decision",
            type="primary"
        )

    if submitted:

        if not reason.strip():

            st.warning(
                "An override reason is required before submitting."
            )

            return None

        return human_decision, reason, note

    return None


def decision_confirmation(entry: dict):

    render_html(
        f"""
        <div style="
            background:{COLORS['risk_low']}14;
            border:1px solid {COLORS['risk_low']}55;
            border-radius:10px;
            padding:1rem 1.2rem;
        ">

            <div style="
                color:{COLORS['risk_low']};
                font-weight:700;
                font-size:0.88rem;
            ">
                Decision recorded
            </div>

            <div style="
                color:{COLORS['text_secondary']};
                font-size:0.78rem;
                margin-top:4px;
            ">
                Memory updated — {entry['memory_update']}
            </div>

            <div style="
                color:{COLORS['text_muted']};
                font-size:0.72rem;
                margin-top:6px;
            ">
                This decision will be available as a precedent
                for future similar alerts.
            </div>

        </div>
        """
    )