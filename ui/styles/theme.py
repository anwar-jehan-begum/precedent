"""
Centralized theme / design system for PRECEDENT.
Premium enterprise dark theme — fintech/security operations aesthetic.
"""

from textwrap import dedent
import streamlit as st

# ---------------------------------------------------------------------------
# Color tokens — used across ALL components
# ---------------------------------------------------------------------------
COLORS = {
    # Backgrounds
    "bg":           "#0B0E14",
    "bg_alt":       "#0D1117",
    "surface":      "#131822",
    "surface_alt":  "#17202E",
    "surface_hi":   "#1C2536",   # slightly elevated surface
    # Borders
    "border":       "#1E2535",
    "border_soft":  "#181F2E",
    "border_hi":    "#2A3347",   # visible separator
    # Typography
    "text_primary":   "#E2E8F4",
    "text_secondary": "#8896B0",
    "text_muted":     "#4B5675",
    "text_faint":     "#303A50",
    # Accent (blue — primary actions, links, active states)
    "accent":        "#3B82F6",
    "accent_soft":   "rgba(59,130,246,0.09)",
    "accent_border": "rgba(59,130,246,0.28)",
    # Risk / status
    "risk_high":        "#EF4444",
    "risk_high_soft":   "rgba(239,68,68,0.09)",
    "risk_medium":      "#F59E0B",
    "risk_medium_soft": "rgba(245,158,11,0.09)",
    "risk_low":         "#10B981",
    "risk_low_soft":    "rgba(16,185,129,0.09)",
}


def render_html(content: str):
    """Render dedented HTML safely via st.html()."""
    st.html(dedent(content))


def risk_color(risk: str) -> str:
    r = (risk or "").upper()
    return COLORS["risk_high"] if r == "HIGH" else (
        COLORS["risk_medium"] if r == "MEDIUM" else COLORS["risk_low"]
    )


def risk_soft(risk: str) -> str:
    r = (risk or "").upper()
    return COLORS["risk_high_soft"] if r == "HIGH" else (
        COLORS["risk_medium_soft"] if r == "MEDIUM" else COLORS["risk_low_soft"]
    )


def status_dot(color: str, glow: bool = False) -> str:
    shadow = f"box-shadow:0 0 6px {color}80;" if glow else ""
    return (
        f'<span style="display:inline-block;width:6px;height:6px;'
        f'border-radius:50%;background:{color};{shadow}"></span>'
    )


def inject_global_css():
    render_html(
        f"""
        <style>
        /* ── Font ── */
        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont,
                         'Segoe UI', system-ui, sans-serif;
            -webkit-font-smoothing: antialiased;
        }}

        /* ── Hide Streamlit chrome ── */
        #MainMenu, header, footer,
        [data-testid="stToolbar"],
        [data-testid="stDecoration"] {{ display: none !important; }}

        /* ── App background ── */
        .stApp {{
            background: {COLORS["bg"]};
        }}

        /* ── Content container ── */
        .block-container {{
            padding-top: 1.8rem;
            padding-bottom: 2.5rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 1380px;
        }}

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {{
            background: {COLORS["bg_alt"]};
            border-right: 1px solid {COLORS["border_soft"]};
        }}
        [data-testid="stSidebar"] > div:first-child {{
            padding-top: 0;
        }}

        /* ── Global text colors ── */
        h1, h2, h3, h4, h5, h6 {{
            color: {COLORS["text_primary"]};
            font-weight: 700;
        }}
        p, span, div, label {{
            color: {COLORS["text_primary"]};
        }}

        /* ── Buttons ── */
        .stButton > button {{
            background: {COLORS["surface_alt"]};
            color: {COLORS["text_secondary"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 7px;
            padding: 0.42rem 1rem;
            font-weight: 500;
            font-size: 0.82rem;
            letter-spacing: 0.01em;
            transition: border-color 0.12s, background 0.12s, color 0.12s;
            box-shadow: none;
        }}
        .stButton > button:hover {{
            border-color: {COLORS["accent_border"]};
            background: {COLORS["accent_soft"]};
            color: {COLORS["accent"]};
        }}
        .stButton > button:focus {{
            outline: 2px solid {COLORS["accent_border"]};
            outline-offset: 2px;
        }}
        .stButton > button[kind="primary"] {{
            background: {COLORS["accent"]};
            border-color: {COLORS["accent"]};
            color: #fff;
            font-weight: 600;
        }}
        .stButton > button[kind="primary"]:hover {{
            background: #2563EB;
            border-color: #2563EB;
            color: #fff;
        }}

        /* ── Inputs ── */
        .stTextInput input,
        .stTextArea textarea {{
            background: {COLORS["surface"]} !important;
            border: 1px solid {COLORS["border"]} !important;
            color: {COLORS["text_primary"]} !important;
            border-radius: 7px !important;
            font-size: 0.83rem !important;
        }}
        .stTextInput input:focus,
        .stTextArea textarea:focus {{
            border-color: {COLORS["accent_border"]} !important;
            box-shadow: 0 0 0 2px {COLORS["accent_soft"]} !important;
        }}
        .stSelectbox [data-baseweb="select"] {{
            background: {COLORS["surface"]} !important;
            border: 1px solid {COLORS["border"]} !important;
            border-radius: 7px !important;
        }}
        .stSelectbox [data-baseweb="select"] > div {{
            background: {COLORS["surface"]} !important;
            color: {COLORS["text_primary"]} !important;
        }}

        /* ── Expanders ── */
        [data-testid="stExpander"] {{
            background: {COLORS["surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 9px;
            overflow: hidden;
        }}
        [data-testid="stExpander"] summary {{
            font-size: 0.83rem;
            font-weight: 500;
            padding: 0.6rem 0.85rem;
            color: {COLORS["text_primary"]};
        }}
        [data-testid="stExpander"] summary:hover {{
            background: {COLORS["surface_alt"]};
        }}
        [data-testid="stExpander"] > div > div {{
            padding: 0.5rem 0.85rem 0.85rem;
        }}

        /* ── Tabs ── */
        [data-testid="stTabs"] [role="tablist"] {{
            border-bottom: 1px solid {COLORS["border"]};
            gap: 0;
        }}
        [data-testid="stTabs"] button[role="tab"] {{
            background: transparent;
            color: {COLORS["text_muted"]};
            border: none;
            border-bottom: 2px solid transparent;
            padding: 0.55rem 1.1rem;
            font-size: 0.82rem;
            font-weight: 500;
            border-radius: 0;
            transition: color 0.12s, border-color 0.12s;
        }}
        [data-testid="stTabs"] button[role="tab"]:hover {{
            color: {COLORS["text_secondary"]};
            background: transparent;
        }}
        [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
            color: {COLORS["text_primary"]};
            border-bottom-color: {COLORS["accent"]};
            font-weight: 600;
        }}

        /* ── Dataframe ── */
        [data-testid="stDataFrame"] {{
            border: 1px solid {COLORS["border"]};
            border-radius: 9px;
            overflow: hidden;
        }}
        [data-testid="stDataFrame"] thead th {{
            background: {COLORS["surface_alt"]} !important;
            color: {COLORS["text_muted"]} !important;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        [data-testid="stDataFrame"] tbody tr:hover td {{
            background: {COLORS["surface_hi"]} !important;
        }}

        /* ── Alerts ── */
        [data-testid="stAlert"] {{
            border-radius: 8px;
            font-size: 0.83rem;
        }}

        /* ── Caption / small text ── */
        .stCaption, small {{
            color: {COLORS["text_muted"]} !important;
            font-size: 0.74rem !important;
        }}

        /* ── Divider ── */
        hr {{
            border: none;
            border-top: 1px solid {COLORS["border_soft"]};
            margin: 1rem 0;
        }}

        /* ── Scrollbar ── */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: {COLORS["bg"]}; }}
        ::-webkit-scrollbar-thumb {{
            background: {COLORS["border_hi"]};
            border-radius: 3px;
        }}
        ::-webkit-scrollbar-thumb:hover {{ background: {COLORS["text_muted"]}; }}

        /* ── Spinner ── */
        [data-testid="stSpinner"] > div {{
            border-top-color: {COLORS["accent"]} !important;
        }}

        /* ── Form ── */
        [data-testid="stForm"] {{
            background: {COLORS["surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 10px;
            padding: 1rem;
        }}

        /* ── Markdown ── */
        .stMarkdown p {{
            font-size: 0.83rem;
            line-height: 1.6;
            color: {COLORS["text_secondary"]};
            margin: 0;
        }}
        .stMarkdown strong {{
            color: {COLORS["text_primary"]};
            font-weight: 600;
        }}
        </style>
        """
    )