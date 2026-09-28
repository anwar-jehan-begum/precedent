"""
Centralized theme / CSS for PRECEDENT.
All custom HTML rendering should go through render_html() which uses
st.html() instead of st.markdown(..., unsafe_allow_html=True) to avoid
indentation / escaping rendering bugs.
"""

from textwrap import dedent

import streamlit as st

# ---------------------------------------------------------------------------
# Color tokens
# ---------------------------------------------------------------------------
COLORS = {
    "bg": "#0B0E14",
    "bg_alt": "#0E1220",
    "surface": "#131826",
    "surface_alt": "#161C2C",
    "border": "#232A3D",
    "border_soft": "#1C2233",
    "text_primary": "#E7EAF2",
    "text_secondary": "#9AA4BF",
    "text_muted": "#5E6784",
    "accent": "#3E8BFF",
    "accent_soft": "rgba(62, 139, 255, 0.12)",
    "accent_border": "rgba(62, 139, 255, 0.35)",
    "risk_high": "#FF5C5C",
    "risk_high_soft": "rgba(255, 92, 92, 0.12)",
    "risk_medium": "#F5B94D",
    "risk_medium_soft": "rgba(245, 185, 77, 0.12)",
    "risk_low": "#3DD68C",
    "risk_low_soft": "rgba(61, 214, 140, 0.12)",
}


def render_html(content: str):
    """Render dedented HTML safely via st.html()."""
    st.html(dedent(content))


def risk_color(risk: str) -> str:
    risk = (risk or "").upper()
    if risk == "HIGH":
        return COLORS["risk_high"]
    if risk == "MEDIUM":
        return COLORS["risk_medium"]
    return COLORS["risk_low"]


def risk_soft(risk: str) -> str:
    risk = (risk or "").upper()
    if risk == "HIGH":
        return COLORS["risk_high_soft"]
    if risk == "MEDIUM":
        return COLORS["risk_medium_soft"]
    return COLORS["risk_low_soft"]


def inject_global_css():
    render_html(
        f"""
        <style>
        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}

        #MainMenu, header, footer {{ visibility: hidden; }}

        .stApp {{
            background: {COLORS["bg"]};
        }}

        [data-testid="stSidebar"] {{
            background: {COLORS["bg_alt"]};
            border-right: 1px solid {COLORS["border_soft"]};
        }}

        [data-testid="stSidebar"] > div:first-child {{
            padding-top: 1.2rem;
        }}

        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1280px;
        }}

        h1, h2, h3, h4, h5, h6, p, span, div, label {{
            color: {COLORS["text_primary"]};
        }}

        .stButton > button {{
            background: {COLORS["surface_alt"]};
            color: {COLORS["text_primary"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            font-size: 0.85rem;
            transition: all 0.15s ease;
        }}

        .stButton > button:hover {{
            border-color: {COLORS["accent_border"]};
            background: {COLORS["accent_soft"]};
            color: {COLORS["accent"]};
        }}

        .stButton > button[kind="primary"] {{
            background: {COLORS["accent"]};
            border: 1px solid {COLORS["accent"]};
            color: white;
        }}

        .stButton > button[kind="primary"]:hover {{
            background: #2f78ea;
        }}

        .stTextInput input, .stSelectbox [data-baseweb="select"], .stTextArea textarea {{
            background: {COLORS["surface"]} !important;
            border: 1px solid {COLORS["border"]} !important;
            color: {COLORS["text_primary"]} !important;
            border-radius: 8px !important;
        }}

        [data-testid="stExpander"] {{
            background: {COLORS["surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 10px;
        }}

        hr {{
            border-color: {COLORS["border_soft"]};
        }}

        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: {COLORS["bg"]}; }}
        ::-webkit-scrollbar-thumb {{ background: {COLORS["border"]}; border-radius: 4px; }}
        </style>
        """
    )