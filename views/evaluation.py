"""Evaluation view: real metrics from dataset + Hindsight + analyst trail."""

from __future__ import annotations

import streamlit as st

from ui.components.metrics import metric_row
from ui.styles.theme import COLORS, render_html


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _badge(available: bool) -> str:
    return (
        f'<span style="font-size:0.65rem;font-weight:700;letter-spacing:0.06em;'
        f'color:{COLORS["risk_low"]};text-transform:uppercase;">MEASURED</span>'
        if available else
        f'<span style="font-size:0.65rem;font-weight:700;letter-spacing:0.06em;'
        f'color:{COLORS["text_muted"]};text-transform:uppercase;">UNAVAILABLE</span>'
    )


def _section_header(title: str, available: bool):
    render_html(
        f"""
        <div style="display:flex;align-items:center;gap:10px;
                    margin-top:1.2rem;margin-bottom:0.5rem;">
            <span style="font-size:0.95rem;font-weight:700;
                         color:{COLORS['text_primary']};">{title}</span>
            {_badge(available)}
        </div>
        """
    )


def _kv(label: str, value: str):
    render_html(
        f"""
        <div style="display:flex;justify-content:space-between;
                    padding:0.4rem 0;border-bottom:1px solid {COLORS['border_soft']};
                    font-size:0.82rem;">
            <span style="color:{COLORS['text_secondary']};">{label}</span>
            <span style="color:{COLORS['text_primary']};font-weight:600;">{value}</span>
        </div>
        """
    )


def _unavailable_box(reason: str):
    render_html(
        f"""
        <div style="background:{COLORS['surface']};border:1px solid {COLORS['border']};
                    border-left:3px solid {COLORS['text_muted']};border-radius:9px;
                    padding:0.75rem 1rem;font-size:0.78rem;
                    color:{COLORS['text_muted']};margin-bottom:0.5rem;">
            Not measured: {reason}
        </div>
        """
    )


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render():
    render_html(
        f"""
        <div style="margin-bottom:1rem;">
            <div style="font-size:1.45rem;font-weight:700;
                        color:{COLORS['text_primary']};">Evaluation</div>
            <div style="font-size:0.82rem;color:{COLORS['text_secondary']};margin-top:4px;">
                Real measured metrics from the HI-Small dataset, alert generator,
                Hindsight memory bank, and session analyst decisions.
                Every number here is computed — not fabricated.
            </div>
        </div>
        """
    )

    with st.spinner("Computing evaluation metrics…"):
        from agent.evaluator import get_evaluation_report
        report = get_evaluation_report()

    ds    = report["dataset"]
    ag    = report["alert_generator"]
    hs    = report["hindsight"]
    ana   = report["analyst"]
    llm   = report["llm_accuracy"]

    # ================================================================
    # TOP METRICS ROW — real values where available
    # ================================================================

    metrics = []

    if ag.get("available"):
        metrics.append({
            "label":    "Alert Generator Precision",
            "value":    f"{ag['precision_pct']}%",
            "sublabel": f"{ag['laundering_alerts']} of {ag['total_alerts']} alerts truly laundering",
            "accent":   COLORS["risk_low"],
        })
    else:
        metrics.append({
            "label":    "Alert Generator Precision",
            "value":    "N/A",
            "sublabel": "Dataset not available",
            "accent":   COLORS["text_muted"],
        })

    if hs.get("available"):
        metrics.append({
            "label":    "Memories in Bank",
            "value":    str(hs["memory_count"]),
            "sublabel": f"Bank: {hs['bank_id']}",
            "accent":   COLORS["accent"],
        })
    else:
        metrics.append({
            "label":    "Memories in Bank",
            "value":    "N/A",
            "sublabel": hs.get("reason", "Hindsight unavailable"),
            "accent":   COLORS["text_muted"],
        })

    if ana.get("available"):
        metrics.append({
            "label":    "Analyst Override Rate",
            "value":    f"{ana['override_rate']}%",
            "sublabel": f"{ana['overrides']} overrides of {ana['total']} decisions",
            "accent":   COLORS["risk_medium"],
        })
    else:
        metrics.append({
            "label":    "Analyst Override Rate",
            "value":    "N/A",
            "sublabel": "No decisions recorded",
            "accent":   COLORS["text_muted"],
        })

    if ds.get("available"):
        metrics.append({
            "label":    "Dataset Laundering Rate",
            "value":    f"{ds['laundering_pct']}%",
            "sublabel": f"{ds['laundering_transactions']:,} of {ds['total_transactions']:,} txns",
            "accent":   COLORS["risk_high"],
        })
    else:
        metrics.append({
            "label":    "Dataset Size",
            "value":    "N/A",
            "sublabel": "Dataset not available",
            "accent":   COLORS["text_muted"],
        })

    metric_row(metrics)
    st.write("")

    # ================================================================
    # DETAILED SECTIONS
    # ================================================================

    col_left, col_right = st.columns(2)

    with col_left:

        # ── Dataset ──────────────────────────────────────────────────
        _section_header("HI-Small Dataset", ds.get("available", False))

        if ds.get("available"):
            _kv("Total transactions", f"{ds['total_transactions']:,}")
            _kv("Laundering transactions", f"{ds['laundering_transactions']:,}")
            _kv("Normal transactions", f"{ds['normal_transactions']:,}")
            _kv("Laundering rate", f"{ds['laundering_pct']}%")
            st.write("")
            st.caption("Top currencies")
            for currency, count in list(ds.get("top_currencies", {}).items())[:4]:
                _kv(currency, f"{count:,} txns")
        else:
            _unavailable_box(ds.get("reason", "unknown"))
            render_html(
                f"""
                <div style="font-size:0.75rem;color:{COLORS['text_muted']};
                            margin-top:0.4rem;">
                    Add <code>data/HI-Small/HI-Small_Trans.csv</code> to enable
                    dataset-derived metrics.
                </div>
                """
            )

        # ── Hindsight ─────────────────────────────────────────────────
        _section_header("Hindsight Memory Bank", hs.get("available", False))

        if hs.get("available"):
            _kv("Bank ID", hs["bank_id"])
            _kv("Memories stored", str(hs["memory_count"]))
            _kv("Health check latency", f"{hs['health_latency_ms']} ms")
            _kv("Recall working", "Yes" if hs.get("recall_ok") else "No")
        else:
            _unavailable_box(hs.get("reason", "unknown"))

    with col_right:

        # ── Alert Generator ───────────────────────────────────────────
        _section_header("Alert Generator Quality", ag.get("available", False))

        if ag.get("available"):
            _kv("Alerts generated", str(ag["total_alerts"]))
            _kv("Truly laundering", str(ag["laundering_alerts"]))
            _kv("Normal (false flags)", str(ag["normal_alerts"]))
            _kv("Precision", f"{ag['precision_pct']}%")
            _kv("Generation time", f"{ag['generation_time_sec']}s")
            st.write("")
            st.caption("Signal distribution")
            for sig, count in list(ag.get("signal_distribution", {}).items())[:5]:
                _kv(sig.replace("_", " ").title(), str(count))
        else:
            _unavailable_box(ag.get("reason", "unknown"))

        # ── Analyst Decisions ─────────────────────────────────────────
        _section_header("Analyst Decisions (This Session)", ana.get("available", False))

        if ana.get("available"):
            if ana["total"] == 0:
                render_html(
                    f"""
                    <div style="font-size:0.78rem;color:{COLORS['text_muted']};">
                        No decisions recorded yet this session.
                        Analyse an alert and accept or override the recommendation.
                    </div>
                    """
                )
            else:
                _kv("Total decisions", str(ana["total"]))
                _kv("Accepted AI recommendation", str(ana["accepts"]))
                _kv("Overrode AI recommendation", str(ana["overrides"]))
                _kv("Override rate", f"{ana['override_rate']}%")
        else:
            _unavailable_box(ana.get("reason", "unknown"))

    # ================================================================
    # LLM ACCURACY — clearly labelled unavailable
    # ================================================================

    st.write("")
    _section_header("LLM Decision Accuracy (Memory ON vs OFF)", False)
    _unavailable_box(llm.get("reason", ""))
    render_html(
        f"""
        <div style="background:{COLORS['surface']};border:1px solid {COLORS['border']};
                    border-radius:10px;padding:0.9rem 1.1rem;
                    font-size:0.78rem;color:{COLORS['text_secondary']};
                    line-height:1.6;margin-top:0.4rem;">
            <strong>To measure LLM accuracy:</strong><br>
            1. Set <code>GROQ_API_KEY</code> in your <code>.env</code> file.<br>
            2. Ensure HI-Small dataset is present at
               <code>data/HI-Small/HI-Small_Trans.csv</code>.<br>
            3. Run <code>python -m agent.evaluator</code> as a standalone batch job.<br>
            4. This will compare <em>Memory OFF</em> (AI alone) vs
               <em>Memory ON</em> (AI + Hindsight recall) across labelled alerts
               and report precision, recall, and false-clear rate against
               <code>is_laundering</code> ground truth — without contaminating
               the live inference path.
        </div>
        """
    )
