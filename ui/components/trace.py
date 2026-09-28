"""Memory trace — the subtle 'thinking' sequence shown when Analyze is clicked."""

import time

import streamlit as st

from ui.styles.theme import COLORS, render_html

TRACE_STAGES = [
    "Retrieving customer memory",
    "Searching historical precedents",
    "Applying typology knowledge",
    "Generating recommendation",
]


def run_memory_trace(placeholder, delay: float = 0.35):
    """Render each stage in sequence inside the given placeholder."""
    for i, stage in enumerate(TRACE_STAGES):
        rows = ""
        for j, s in enumerate(TRACE_STAGES):
            if j < i:
                icon, color = "✓", COLORS["risk_low"]
            elif j == i:
                icon, color = "○", COLORS["accent"]
            else:
                icon, color = "·", COLORS["text_muted"]
            weight = "600" if j <= i else "400"
            rows += f"""
            <div style="display:flex; align-items:center; gap:10px; padding:4px 0;">
                <span style="color:{color}; width:16px; text-align:center; font-size:0.85rem;">{icon}</span>
                <span style="color:{color}; font-size:0.8rem; font-weight:{weight};">{s}</span>
            </div>
            """
        with placeholder:
            render_html(
                f"""
                <div style="
                    background:{COLORS['surface']};
                    border:1px solid {COLORS['border']};
                    border-radius:10px;
                    padding: 0.9rem 1.1rem;
                ">
                    <div style="font-size:0.68rem; color:{COLORS['text_muted']}; letter-spacing:0.06em; text-transform:uppercase; margin-bottom:6px;">
                        Memory Trace
                    </div>
                    {rows}
                </div>
                """
            )
        time.sleep(delay)