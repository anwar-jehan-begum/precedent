"""Reusable KPI / metric card components."""

import streamlit as st
from ui.styles.theme import COLORS, render_html


def metric_row(metrics: list):
    """
    metrics: list of {
        "label": str,
        "value": str,
        "accent": optional hex,
        "sublabel": optional str,
        "icon": optional str (single char / emoji)
    }
    Renders evenly spaced metric cards with left accent border.
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        accent = m.get("accent", COLORS["accent"])
        icon_html = (
            f'<span style="font-size:1rem;opacity:0.55;float:right;">{m["icon"]}</span>'
            if m.get("icon") else ""
        )
        sub_html = (
            f'<div style="font-size:0.7rem;color:{COLORS["text_muted"]};'
            f'margin-top:3px;line-height:1.4;">{m["sublabel"]}</div>'
            if m.get("sublabel") else ""
        )
        with col:
            render_html(
                f"""
                <div style="
                    background:{COLORS['surface']};
                    border:1px solid {COLORS['border']};
                    border-left:3px solid {accent};
                    border-radius:9px;
                    padding:1rem 1.15rem 0.9rem;
                ">
                    {icon_html}
                    <div style="
                        font-size:0.63rem;
                        font-weight:700;
                        color:{COLORS['text_muted']};
                        letter-spacing:0.09em;
                        text-transform:uppercase;
                    ">{m['label']}</div>
                    <div style="
                        font-size:1.65rem;
                        font-weight:700;
                        color:{COLORS['text_primary']};
                        margin-top:4px;
                        line-height:1;
                        font-variant-numeric:tabular-nums;
                    ">{m['value']}</div>
                    {sub_html}
                </div>
                """
            )


def stat_pill(label: str, value: str, color: str):
    render_html(
        f"""
        <span style="
            display:inline-flex;align-items:center;gap:5px;
            background:{color}14;color:{color};
            border:1px solid {color}40;border-radius:999px;
            padding:2px 9px;font-size:0.7rem;font-weight:600;
        ">
            {label}: {value}
        </span>
        """
    )


def badge(text: str, color: str, soft: str):
    """Small risk/status badge."""
    return (
        f'<span style="display:inline-block;background:{soft};color:{color};'
        f'border:1px solid {color}44;border-radius:5px;'
        f'padding:1px 8px;font-size:0.65rem;font-weight:700;letter-spacing:0.04em;">'
        f'{text}</span>'
    )