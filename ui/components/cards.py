"""Alert queue card component."""

import streamlit as st
from ui.styles.theme import COLORS, render_html, risk_color, risk_soft


def _fmt_amount(amount: float, currency: str = "USD") -> str:
    """Format amount with currency symbol and comma separators."""
    sym = {"USD": "$", "EUR": "€", "GBP": "£", "INR": "₹"}.get(currency.upper(), "")
    if amount >= 1_000_000:
        return f"{sym}{amount/1_000_000:.1f}M"
    if amount >= 1_000:
        return f"{sym}{amount:,.0f}"
    return f"{sym}{amount:.2f}"


def alert_card(alert: dict, on_analyze):
    risk     = alert["risk"]
    color    = risk_color(risk)
    soft     = risk_soft(risk)
    currency = alert.get("currency", "USD")
    amount   = _fmt_amount(float(alert.get("amount", 0)), currency)
    signals  = alert.get("signals", [])
    sig_html = "  ·  ".join(
        f'<span style="color:{COLORS["text_secondary"]}">{s}</span>'
        for s in signals[:3]
    )
    if len(signals) > 3:
        sig_html += f'  <span style="color:{COLORS["text_faint"]}">+{len(signals)-3} more</span>'

    render_html(
        f"""
        <div style="
            background:{COLORS['surface']};
            border:1px solid {COLORS['border']};
            border-left:3px solid {color};
            border-radius:9px;
            padding:0.95rem 1.2rem 0.85rem;
            margin-bottom:0.45rem;
            transition:border-color 0.15s;
        ">
            <div style="display:flex;justify-content:space-between;
                        align-items:flex-start;gap:10px;flex-wrap:wrap;">
                <div>
                    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                        <span style="font-size:0.8rem;font-weight:700;
                                     color:{COLORS['text_primary']};font-variant-numeric:tabular-nums;">
                            {alert['id']}
                        </span>
                        <span style="font-size:0.75rem;color:{COLORS['text_secondary']};">
                            {alert['customer']}
                        </span>
                    </div>
                    <div style="margin-top:5px;display:flex;align-items:center;gap:12px;">
                        <span style="font-size:0.88rem;font-weight:700;
                                     color:{COLORS['text_primary']};font-variant-numeric:tabular-nums;">
                            {amount}
                        </span>
                        <span style="font-size:0.72rem;color:{COLORS['text_muted']};">
                            {currency}
                        </span>
                        <span style="font-size:0.72rem;color:{COLORS['text_secondary']};">
                            {alert.get('typology','—')}
                        </span>
                    </div>
                </div>
                <div style="
                    background:{soft};color:{color};
                    border:1px solid {color}44;border-radius:5px;
                    padding:2px 9px;font-size:0.65rem;font-weight:700;
                    letter-spacing:0.06em;white-space:nowrap;align-self:flex-start;
                ">{risk}</div>
            </div>
            <div style="margin-top:0.65rem;font-size:0.72rem;
                        color:{COLORS['text_muted']};line-height:1.5;">
                {sig_html if sig_html else '<span style="color:{COLORS[\'text_faint\']}">No signals</span>'}
            </div>
        </div>
        """
    )

    col_space, col_btn = st.columns([6, 1])
    with col_btn:
        if st.button(
            "Analyze",
            key=f"analyze_{alert['id']}",
            use_container_width=True,
            type="primary",
        ):
            on_analyze(alert["id"])