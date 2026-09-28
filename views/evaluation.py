"""Evaluation view: memory ON vs OFF comparison."""

import plotly.graph_objects as go
import streamlit as st

from data.mock_data import get_evaluation_metrics
from ui.components.metrics import metric_row
from ui.styles.theme import COLORS, render_html


def _make_comparison_chart(
    title: str,
    without_value: float,
    with_value: float,
    unit: str,
    higher_is_better: bool,
):
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Without Memory",
            x=["Without Memory"],
            y=[without_value],
            marker_color=COLORS["text_muted"],
            text=[f"{without_value}{unit}"],
            textposition="outside",
            hovertemplate=f"Without Memory: %{{y}}{unit}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Bar(
            name="With PRECEDENT",
            x=["With PRECEDENT"],
            y=[with_value],
            marker_color=COLORS["accent"],
            text=[f"{with_value}{unit}"],
            textposition="outside",
            hovertemplate=f"With PRECEDENT: %{{y}}{unit}<extra></extra>",
        )
    )

    max_value = max(without_value, with_value)

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(
                color=COLORS["text_primary"],
                size=15,
            ),
            x=0,
        ),
        barmode="group",
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color=COLORS["text_secondary"],
            size=11,
        ),
        showlegend=False,
        margin=dict(
            l=10,
            r=10,
            t=55,
            b=10,
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS["border_soft"],
            zeroline=False,
            range=[0, max_value * 1.25 if max_value else 1],
            title=unit if unit else None,
        ),
        height=270,
    )

    return fig


def _make_recall_chart(metrics):
    labels = ["Illicit-Case Recall", "Safe-Clear Rate"]
    without_values = [
        metrics["illicit_recall"]["without"],
        metrics["safe_clear_rate"]["without"],
    ]
    with_values = [
        metrics["illicit_recall"]["with"],
        metrics["safe_clear_rate"]["with"],
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Without Memory",
            y=labels,
            x=without_values,
            orientation="h",
            marker_color=COLORS["text_muted"],
            text=[f"{v}%" for v in without_values],
            textposition="outside",
            hovertemplate="Without Memory: %{x}%<extra></extra>",
        )
    )

    fig.add_trace(
        go.Bar(
            name="With PRECEDENT",
            y=labels,
            x=with_values,
            orientation="h",
            marker_color=COLORS["accent"],
            text=[f"{v}%" for v in with_values],
            textposition="outside",
            hovertemplate="With PRECEDENT: %{x}%<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(
            text="Outcome Quality",
            font=dict(
                color=COLORS["text_primary"],
                size=15,
            ),
            x=0,
        ),
        barmode="group",
        plot_bgcolor=COLORS["surface"],
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color=COLORS["text_secondary"],
            size=11,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(
            l=10,
            r=35,
            t=65,
            b=10,
        ),
        xaxis=dict(
            range=[0, 105],
            gridcolor=COLORS["border_soft"],
            title="Percentage",
        ),
        yaxis=dict(
            gridcolor="rgba(0,0,0,0)",
        ),
        height=300,
    )

    return fig


def render():
    render_html(
        f"""
        <div style="margin-bottom:1rem;">
            <div style="
                font-size:1.45rem;
                font-weight:700;
                color:{COLORS['text_primary']};
            ">
                Evaluation
            </div>

            <div style="
                font-size:0.82rem;
                color:{COLORS['text_secondary']};
                margin-top:4px;
            ">
                Does memory actually help? Compare decision support
                without PRECEDENT against decision support with PRECEDENT.
            </div>
        </div>
        """
    )

    st.warning(
        "DEMO / MOCK VALUES — for hackathon demonstration only. "
        "These are not measured production results.",
        icon="⚠️",
    )

    metrics = get_evaluation_metrics()

    # ========================================================
    # HEADLINE METRICS
    # ========================================================

    metric_row(
        [
            {
                "label": "Illicit-Case Recall",
                "value": f"{metrics['illicit_recall']['with']}%",
                "sublabel": (
                    f"vs {metrics['illicit_recall']['without']}% "
                    "without memory"
                ),
                "accent": COLORS["risk_low"],
            },
            {
                "label": "False-Clear Rate",
                "value": f"{metrics['false_clear_rate']['with']}%",
                "sublabel": (
                    f"vs {metrics['false_clear_rate']['without']}% "
                    "without memory"
                ),
                "accent": COLORS["risk_high"],
            },
            {
                "label": "Avg Reasoning Time",
                "value": f"{metrics['avg_reasoning_time_sec']['with']}s",
                "sublabel": (
                    f"vs {metrics['avg_reasoning_time_sec']['without']}s "
                    "without memory"
                ),
                "accent": COLORS["accent"],
            },
            {
                "label": "Precedents Retrieved",
                "value": f"{metrics['precedents_retrieved_avg']['with']}",
                "sublabel": "average per alert with memory",
                "accent": COLORS["risk_medium"],
            },
        ]
    )

    st.write("")

    # ========================================================
    # VISUAL COMPARISON
    # ========================================================

    col_left, col_right = st.columns(2)

    with col_left:
        st.plotly_chart(
            _make_recall_chart(metrics),
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

    with col_right:
        st.plotly_chart(
            _make_comparison_chart(
                "False-Clear Rate",
                metrics["false_clear_rate"]["without"],
                metrics["false_clear_rate"]["with"],
                "%",
                higher_is_better=False,
            ),
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

    col_left, col_right = st.columns(2)

    with col_left:
        st.plotly_chart(
            _make_comparison_chart(
                "Average Reasoning Time",
                metrics["avg_reasoning_time_sec"]["without"],
                metrics["avg_reasoning_time_sec"]["with"],
                "s",
                higher_is_better=False,
            ),
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

    with col_right:
        st.plotly_chart(
            _make_comparison_chart(
                "Precedents Retrieved",
                metrics["precedents_retrieved_avg"]["without"],
                metrics["precedents_retrieved_avg"]["with"],
                "",
                higher_is_better=True,
            ),
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

    # ========================================================
    # INTERPRETATION STRIP
    # ========================================================

    render_html(
        f"""
        <div style="
            margin-top:0.8rem;
            background:{COLORS['surface']};
            border:1px solid {COLORS['border']};
            border-radius:10px;
            padding:0.9rem 1.1rem;
        ">

            <div style="
                font-size:0.68rem;
                color:{COLORS['text_muted']};
                text-transform:uppercase;
                letter-spacing:0.06em;
            ">
                Memory Signal
            </div>

            <div style="
                margin-top:5px;
                font-size:0.82rem;
                color:{COLORS['text_secondary']};
                line-height:1.55;
            ">
                The demo illustrates how historical precedents can be surfaced
                alongside a current alert. Replace these demo values with the
                measured results from Member 2's evaluation pipeline before
                presenting them as project results.
            </div>

        </div>
        """
    )
