"""AI recommendation card + analyst accept/override workflow."""

import streamlit as st
from ui.styles.theme import COLORS, render_html, risk_color


def recommendation_card(decision: dict):
    rec        = decision["recommendation"]
    confidence = decision.get("confidence") or 0
    reason     = decision.get("reason", "")
    risk_lvl   = decision.get("risk_level", "MEDIUM")

    is_escalate = rec == "ESCALATE"
    dec_color   = COLORS["risk_high"] if is_escalate else COLORS["risk_low"]
    dec_soft    = "rgba(239,68,68,0.07)" if is_escalate else "rgba(16,185,129,0.07)"
    dec_icon    = "▲" if is_escalate else "✓"

    risk_color_val = risk_color(risk_lvl)

    # Confidence bar width
    bar_w = min(100, max(0, int(confidence)))

    render_html(
        f"""
        <div style="
            background:{COLORS['surface']};
            border:1px solid {COLORS['border']};
            border-radius:10px;
            overflow:hidden;
        ">
            <!-- Decision header -->
            <div style="
                background:{dec_soft};
                border-bottom:1px solid {dec_color}30;
                padding:1rem 1.2rem 0.85rem;
            ">
                <div style="
                    font-size:0.6rem;font-weight:700;
                    color:{COLORS['text_muted']};
                    letter-spacing:0.1em;text-transform:uppercase;
                    margin-bottom:6px;
                ">PRECEDENT Recommends</div>

                <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                    <span style="
                        font-size:1.55rem;font-weight:800;
                        color:{dec_color};letter-spacing:0.02em;
                    ">{dec_icon} {rec}</span>
                    <span style="
                        background:{risk_color_val}18;color:{risk_color_val};
                        border:1px solid {risk_color_val}40;
                        border-radius:4px;padding:1px 7px;
                        font-size:0.62rem;font-weight:700;letter-spacing:0.06em;
                    ">{risk_lvl}</span>
                </div>

                <!-- Confidence bar -->
                <div style="margin-top:0.75rem;">
                    <div style="
                        display:flex;justify-content:space-between;
                        font-size:0.67rem;color:{COLORS['text_muted']};
                        margin-bottom:4px;
                    ">
                        <span>Confidence</span>
                        <span style="font-weight:600;color:{dec_color};">{confidence}%</span>
                    </div>
                    <div style="
                        background:{COLORS['surface_alt']};
                        border-radius:999px;height:4px;overflow:hidden;
                    ">
                        <div style="
                            background:{dec_color};
                            width:{bar_w}%;height:100%;
                            border-radius:999px;
                            transition:width 0.4s ease;
                        "></div>
                    </div>
                </div>
            </div>

            <!-- Reason preview -->
            <div style="padding:0.85rem 1.2rem;">
                <div style="
                    font-size:0.63rem;font-weight:700;
                    color:{COLORS['text_muted']};
                    letter-spacing:0.08em;text-transform:uppercase;
                    margin-bottom:6px;
                ">Evidence Summary</div>
                <div style="
                    font-size:0.79rem;
                    color:{COLORS['text_secondary']};
                    line-height:1.6;
                ">{reason[:280]}{'…' if len(reason) > 280 else ''}</div>
            </div>
        </div>
        """
    )


def review_actions(alert_id: str):
    """
    Renders Accept / Override buttons.
    Returns: None | "accept" | "override"
    """
    col1, col2 = st.columns(2)
    action = None
    with col1:
        if st.button(
            "✓  Accept Recommendation",
            key=f"accept_{alert_id}",
            use_container_width=True,
            type="primary",
        ):
            action = "accept"
    with col2:
        if st.button(
            "↩  Override Decision",
            key=f"override_{alert_id}",
            use_container_width=True,
        ):
            action = "override"
    return action


def override_form(alert_id: str, ai_recommendation: str):
    """
    Renders the override form.
    Returns (human_decision, reason, note) or None.
    """
    with st.form(key=f"override_form_{alert_id}"):
        st.markdown(f"**Override — AI recommended {ai_recommendation}**")

        human_decision = st.selectbox(
            "Your decision",
            options=["CLEAR", "ESCALATE"],
            index=1 if ai_recommendation == "CLEAR" else 0,
            key=f"human_decision_{alert_id}",
        )
        reason = st.text_area(
            "Override reason  *(required)*",
            key=f"reason_{alert_id}",
            height=80,
            placeholder="Explain why you are overriding the AI recommendation…",
        )
        note = st.text_area(
            "Analyst note  *(optional)*",
            key=f"note_{alert_id}",
            height=60,
            placeholder="Additional context for the record…",
        )
        submitted = st.form_submit_button("Submit Decision", type="primary")

    if submitted:
        if not reason.strip():
            st.warning("An override reason is required before submitting.", icon="⚠️")
            return None
        return human_decision, reason, note
    return None


def decision_confirmation(entry: dict):
    mem_update = entry.get("memory_update", "Decision stored.")
    is_override = entry.get("override", False)
    final = entry.get("final_decision", "")
    dec_color = COLORS["risk_high"] if final == "ESCALATE" else COLORS["risk_low"]

    render_html(
        f"""
        <div style="
            background:{COLORS['risk_low']}0D;
            border:1px solid {COLORS['risk_low']}40;
            border-left:3px solid {COLORS['risk_low']};
            border-radius:9px;
            padding:0.9rem 1.1rem;
        ">
            <div style="
                display:flex;align-items:center;gap:8px;
                font-size:0.8rem;font-weight:700;color:{COLORS['risk_low']};
                margin-bottom:4px;
            ">
                ✓ Decision Recorded
                {"<span style='background:#F59E0B18;color:#F59E0B;border:1px solid #F59E0B40;"
                 "border-radius:4px;padding:1px 7px;font-size:0.62rem;font-weight:700;"
                 "letter-spacing:0.05em;margin-left:6px;'>OVERRIDE</span>"
                 if is_override else ""}
            </div>
            <div style="font-size:0.76rem;color:{COLORS['text_secondary']};line-height:1.5;">
                {mem_update}
            </div>
            <div style="
                margin-top:6px;font-size:0.7rem;color:{COLORS['text_muted']};
            ">
                This decision is now available as institutional precedent
                for future similar alerts.
            </div>
        </div>
        """
    )