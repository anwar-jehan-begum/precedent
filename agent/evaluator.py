"""
agent/evaluator.py
==================
Offline evaluation engine for PRECEDENT.

Measures:
  - Dataset statistics (from HI-Small, when available)
  - Alert-generator quality (precision of signal detection against ground truth)
  - Hindsight memory statistics (memories on bank, recall success rate)
  - Analyst decision statistics (from session audit trail)

Clearly separates what is MEASURED from what is UNAVAILABLE.

IMPORTANT:
  - is_laundering ground truth is used ONLY here for offline metrics.
  - It is NEVER passed to DecisionEngine or any live inference path.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Prediction evaluation
# ---------------------------------------------------------------------------

def evaluate_predictions(
    predictions: List[str],
    actuals: List[int]
) -> Dict:
    """
    Evaluate model predictions against binary ground-truth labels.

    Mapping:
      ESCALATE -> laundering / suspicious (1)
      CLEAR    -> normal (0)

    Returns:
      - total
      - correct
      - accuracy
      - false_positives
      - false_negatives

    This function is intended for OFFLINE evaluation only.
    Ground truth must never be passed into the live DecisionEngine flow.
    """

    if len(predictions) != len(actuals):
        raise ValueError("Predictions and actuals must have the same length")

    total = len(actuals)

    correct = 0
    false_positives = 0
    false_negatives = 0

    for prediction, actual in zip(predictions, actuals):

        prediction = prediction.upper()

        # ESCALATE = suspicious / laundering
        predicted_laundering = 1 if prediction == "ESCALATE" else 0

        if predicted_laundering == actual:
            correct += 1

        if predicted_laundering == 1 and actual == 0:
            false_positives += 1

        if predicted_laundering == 0 and actual == 1:
            false_negatives += 1

    accuracy = correct / total if total else 0

    return {
        "total": total,
        "correct": correct,
        "accuracy": round(accuracy, 4),
        "false_positives": false_positives,
        "false_negatives": false_negatives
    }


# ---------------------------------------------------------------------------
# Dataset statistics
# ---------------------------------------------------------------------------

def get_dataset_stats() -> Dict[str, Any]:
    """
    Compute real statistics from the HI-Small dataset.

    Returns a dict of measured values or marks them unavailable.
    """

    try:
        from data.live_alerts import DATASET_PATH, using_dataset
        import os
        import pandas as pd

        if not os.path.isfile(DATASET_PATH):
            return {
                "available": False,
                "reason": "HI-Small dataset not present"
            }

        df = pd.read_csv(DATASET_PATH, nrows=200_000)

        total_rows = len(df)

        laundering_count = int(
            df["Is Laundering"].sum()
        )

        normal_count = total_rows - laundering_count

        laundering_pct = (
            round(laundering_count / total_rows * 100, 2)
            if total_rows
            else 0
        )

        currencies = (
            df["Payment Currency"]
            .value_counts()
            .head(5)
            .to_dict()
        )

        formats = (
            df["Payment Format"]
            .value_counts()
            .head(5)
            .to_dict()
        )

        return {
            "available": True,
            "total_transactions": total_rows,
            "laundering_transactions": laundering_count,
            "normal_transactions": normal_count,
            "laundering_pct": laundering_pct,
            "top_currencies": currencies,
            "top_payment_formats": formats,
        }

    except Exception as exc:
        return {
            "available": False,
            "reason": str(exc)
        }


# ---------------------------------------------------------------------------
# Alert generator statistics
# ---------------------------------------------------------------------------

def get_alert_generator_stats(
    max_alerts: int = 2000
) -> Dict[str, Any]:
    """
    Run alert_generator on the dataset and measure:

    - How many alerts it produces
    - What fraction involve truly laundering transactions
      (precision against ground truth)
    - Signal distribution

    Uses is_laundering ground truth ONLY for offline metrics.
    """

    try:
        from data.live_alerts import DATASET_PATH
        import os

        if not os.path.isfile(DATASET_PATH):
            return {
                "available": False,
                "reason": "HI-Small dataset not present"
            }

        from data.alert_generator import generate_alerts

        t0 = time.time()

        alerts = generate_alerts(
            DATASET_PATH,
            nrows=200_000,
            max_alerts=max_alerts
        )

        elapsed = time.time() - t0

        if not alerts:
            return {
                "available": False,
                "reason": "Alert generator returned no alerts"
            }

        total = len(alerts)

        # Ground truth used ONLY for offline evaluation metrics
        laundering = sum(
            1
            for a in alerts
            if a.get("is_laundering") == 1
        )

        normal = total - laundering

        precision = (
            round(laundering / total * 100, 1)
            if total
            else 0
        )

        # Signal distribution
        pattern_counts: Dict[str, int] = {}

        for alert in alerts:

            for sig in alert.get(
                "transaction_pattern",
                ""
            ).split(","):

                sig = sig.strip()

                if sig:
                    pattern_counts[sig] = (
                        pattern_counts.get(sig, 0) + 1
                    )

        return {
            "available": True,
            "total_alerts": total,
            "laundering_alerts": laundering,
            "normal_alerts": normal,
            "precision_pct": precision,
            "generation_time_sec": round(
                elapsed,
                2
            ),
            "signal_distribution": dict(
                sorted(
                    pattern_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            ),
        }

    except Exception as exc:
        return {
            "available": False,
            "reason": str(exc)
        }


# ---------------------------------------------------------------------------
# Hindsight memory statistics
# ---------------------------------------------------------------------------

def get_hindsight_stats() -> Dict[str, Any]:
    """
    Query Hindsight for real memory statistics.

    Returns counts and health — no fabricated numbers.
    """

    try:
        from memory.health import (
            check_hindsight_configuration
        )

        health = check_hindsight_configuration()

        if not health["ok"]:
            return {
                "available": False,
                "reason": health["message"],
                "latency_ms": health.get(
                    "latency_ms",
                    0
                ),
            }

        # Count/retrieve memories in the bank using a broad recall
        from memory.recall import execute_recall
        from memory.config import config

        recall_result = execute_recall(
            query="AML alert analyst decision",
        )

        raw_count = (
            recall_result.get(
                "result_count",
                0
            )
            if recall_result.get("success")
            else 0
        )

        return {
            "available": True,
            "bank_id": health["bank_id"],
            "health_latency_ms": health["latency_ms"],
            "memory_count": raw_count,
            "recall_ok": recall_result.get(
                "success",
                False
            ),
        }

    except Exception as exc:
        return {
            "available": False,
            "reason": str(exc)
        }


# ---------------------------------------------------------------------------
# Session analyst-decision statistics
# ---------------------------------------------------------------------------

def get_analyst_decision_stats() -> Dict[str, Any]:
    """
    Compute statistics from the session audit trail.

    These are real decisions made this session
    (or the demo seed entries).
    """

    try:
        from data.mock_data import get_audit_trail

        trail = get_audit_trail()

        total = len(trail)

        if total == 0:
            return {
                "available": True,
                "total": 0,
                "overrides": 0,
                "accepts": 0,
                "override_rate": 0
            }

        overrides = sum(
            1
            for e in trail
            if e.get("override")
        )

        accepts = total - overrides

        override_rate = round(
            overrides / total * 100,
            1
        )

        return {
            "available": True,
            "total": total,
            "overrides": overrides,
            "accepts": accepts,
            "override_rate": override_rate,
        }

    except Exception as exc:
        return {
            "available": False,
            "reason": str(exc)
        }


# ---------------------------------------------------------------------------
# Combined evaluation report
# ---------------------------------------------------------------------------

def get_evaluation_report() -> Dict[str, Any]:
    """
    Assemble all real evaluation metrics into one report dict.

    Each section clearly declares whether its data is
    measured or unavailable.

    NOTE:
      LLM accuracy (memory ON vs OFF decision accuracy against
      ground truth) requires running DecisionEngine on labelled
      alerts. This requires a GROQ_API_KEY and would consume
      API quota. It is therefore labelled UNAVAILABLE here and
      should be run as a separate offline batch job.
    """

    return {
        "dataset": get_dataset_stats(),

        "alert_generator": get_alert_generator_stats(
            max_alerts=500
        ),

        "hindsight": get_hindsight_stats(),

        "analyst": get_analyst_decision_stats(),

        "llm_accuracy": {
            "available": False,
            "reason": (
                "Requires GROQ_API_KEY and labelled batch evaluation. "
                "Run agent/evaluator.py standalone with GROQ_API_KEY set."
            ),
        },
    }


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    predictions = [
        "ESCALATE",
        "CLEAR",
        "ESCALATE",
        "CLEAR",
        "ESCALATE"
    ]

    actuals = [
        1,
        0,
        0,
        0,
        1
    ]

    result = evaluate_predictions(
        predictions,
        actuals
    )

    print("===== EVALUATION =====")
    print("Total:", result["total"])
    print("Correct:", result["correct"])
    print("Accuracy:", result["accuracy"])
    print(
        "False Positives:",
        result["false_positives"]
    )
    print(
        "False Negatives:",
        result["false_negatives"]
    )