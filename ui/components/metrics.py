"""Reusable KPI / metric card components."""

import streamlit as st

from ui.styles.theme import COLORS, render_html


def metric_row(metrics: list[dict]):
    """
    metrics: list of {
        "label": str,
        "value": str,
        "accent": optional hex color,
        "sublabel": optional str
    }

    Renders an evenly spaced row of metric cards.
    """
    cols = st.columns(len(metrics))

    for col, m in zip(cols, metrics):

        accent = m.get(
            "accent",
            COLORS["accent"]
        )

        with col:

            render_html(
                f"""
                <div style="
                    background: {COLORS['surface']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 12px;
                    padding: 1.1rem 1.2rem;
                    border-top: 2px solid {accent};
                ">

                    <div style="
                        font-size: 0.7rem;
                        color: {COLORS['text_secondary']};
                        letter-spacing: 0.06em;
                        text-transform: uppercase;
                    ">
                        {m['label']}
                    </div>

                    <div style="
                        font-size: 1.7rem;
                        font-weight: 700;
                        color: {COLORS['text_primary']};
                        margin-top: 6px;
                    ">
                        {m['value']}
                    </div>

                    {
                        f'''
                        <div style="
                            font-size:0.72rem;
                            color:{COLORS["text_muted"]};
                            margin-top:2px;
                        ">
                            {m["sublabel"]}
                        </div>
                        '''
                        if m.get("sublabel")
                        else ""
                    }

                </div>
                """
            )


def stat_pill(
    label: str,
    value: str,
    color: str
):
    render_html(
        f"""
        <span style="
            display:inline-flex;
            align-items:center;
            gap:6px;
            background:{color}22;
            color:{color};
            border:1px solid {color}55;
            border-radius:999px;
            padding:3px 10px;
            font-size:0.72rem;
            font-weight:600;
        ">
            {label}: {value}
        </span>
        """
    )