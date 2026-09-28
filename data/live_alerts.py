"""
data/live_alerts.py
====================
Single source of truth for the PRECEDENT alert queue.

MODES
-----
DATASET mode  (using_dataset() == True)
    HI-Small_Trans.csv is present at DATASET_PATH.
    generate_alerts() runs over it, is_laundering is stripped from all
    public-facing dicts.  This is the REQUIRED production/demo mode.

DEMO mode  (using_dataset() == False)
    DATASET_PATH is absent.
    get_alerts() returns an empty list and using_dataset() returns False.
    The UI must display a clear "dataset missing" blocker — it must NOT
    silently serve mock alerts as real data.
    The only mock-data calls permitted are in the evaluation-only
    get_all_with_ground_truth() fallback path, clearly labelled.

IMPORTANT
---------
- is_laundering is NEVER included in any dict returned by get_alerts()
  or get_alert().
- It is accessible ONLY via get_alert_with_ground_truth() and
  get_all_with_ground_truth(), for OFFLINE EVALUATION ONLY.
- Those functions must never be called from views/, integration/, or agent/.
"""

from __future__ import annotations

import os
import functools
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Path
# ---------------------------------------------------------------------------

DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "HI-Small", "HI-Small_Trans.csv"
)

# Alerts loaded per UI session — large enough to be interesting,
# small enough for fast startup.
MAX_UI_ALERTS = 25

# ---------------------------------------------------------------------------
# Signal → typology mapping
# ---------------------------------------------------------------------------

_TYPOLOGY_MAP = {
    "high_value_transaction":  "High-Value Transaction",
    "rapid_movement":          "Rapid Movement",
    "multiple_transfers":      "Rapid Movement",
    "multiple_counterparties": "Multiple Counterparties",
}

_TYPOLOGY_PRIORITY = [
    "multiple_counterparties",
    "rapid_movement",
    "multiple_transfers",
    "high_value_transaction",
]


def _signals_to_typology(transaction_pattern: str) -> str:
    signals = [s.strip() for s in transaction_pattern.split(",")]
    for sig in _TYPOLOGY_PRIORITY:
        if sig in signals:
            return _TYPOLOGY_MAP[sig]
    if signals:
        return _TYPOLOGY_MAP.get(signals[0], signals[0].replace("_", " ").title())
    return "Unknown"


def _signals_to_risk(signals: List[str], amount: float) -> str:
    score = 0
    if "multiple_counterparties" in signals:
        score += 2
    if "rapid_movement" in signals or "multiple_transfers" in signals:
        score += 1
    if "high_value_transaction" in signals:
        score += 2
    if amount >= 500_000:
        score += 1
    if score >= 4:
        return "HIGH"
    if score >= 2:
        return "MEDIUM"
    return "LOW"


def _signal_to_label(signal: str) -> str:
    return {
        "high_value_transaction":  "High-value transaction detected",
        "rapid_movement":          "Rapid fund movement pattern",
        "multiple_transfers":      "Multiple transfers in short window",
        "multiple_counterparties": "Multiple new counterparties",
    }.get(signal, signal.replace("_", " ").title())


def _normalise(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert an alert_generator alert dict to the UI alert schema.
    is_laundering is intentionally NOT included.

    UI schema used by alerts.py, app.py, cards.py:
        id, alert_id, customer, customer_id, amount, currency,
        typology, risk, signals, precedent_count, confidence,
        status, geography, timestamp, from_bank, to_bank,
        counterparty, payment_format, transaction_pattern
    """
    signals_raw = [s.strip() for s in raw.get("transaction_pattern", "").split(",")]
    typology = _signals_to_typology(raw.get("transaction_pattern", ""))
    risk = _signals_to_risk(signals_raw, float(raw.get("amount", 0)))

    return {
        "id":          raw["alert_id"],
        "alert_id":    raw["alert_id"],
        "customer_id": raw["customer_id"],
        "customer":    f"Account {raw['customer_id']}",
        "amount":      float(raw.get("amount", 0)),
        "currency":    raw.get("currency", "USD"),
        "typology":    typology,
        "risk":        risk,
        "signals":     [_signal_to_label(s) for s in signals_raw if s],
        "precedent_count":     0,
        "confidence":          0,
        "status":              "OPEN",
        "geography":           [f"Bank {raw.get('from_bank','?')} → Bank {raw.get('to_bank','?')}"],
        "timestamp":           raw.get("timestamp", ""),
        "from_bank":           raw.get("from_bank", ""),
        "to_bank":             raw.get("to_bank", ""),
        "counterparty":        raw.get("counterparty", ""),
        "payment_format":      raw.get("payment_format", ""),
        "transaction_pattern": raw.get("transaction_pattern", ""),
        # Deliberately absent: is_laundering
    }


# ---------------------------------------------------------------------------
# Dataset loading — cached per process
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=1)
def _load_dataset_alerts() -> Optional[List[Dict[str, Any]]]:
    """
    Try to load RAW alerts (including is_laundering) from HI-Small.
    Returns:
        list of raw alert dicts   — dataset present and loaded successfully
        None                      — dataset absent or load failed
    Raw dicts are NEVER returned to callers outside this module.
    """
    if not os.path.isfile(DATASET_PATH):
        return None
    try:
        from data.alert_generator import generate_alerts
        raw = generate_alerts(
            file_path=DATASET_PATH,
            nrows=200_000,
            max_alerts=MAX_UI_ALERTS,
        )
        return raw if raw else None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Status helpers
# ---------------------------------------------------------------------------

def using_dataset() -> bool:
    """True  → HI-Small loaded, UI in DATASET mode (real data).
       False → dataset absent, UI in DEMO mode (empty queue)."""
    return _load_dataset_alerts() is not None


def dataset_alert_count() -> int:
    """Number of alerts loaded from the dataset (0 if absent)."""
    raw = _load_dataset_alerts()
    return len(raw) if raw else 0


# ---------------------------------------------------------------------------
# Public alert API — NO mock fallback
# ---------------------------------------------------------------------------

def get_alerts() -> List[Dict[str, Any]]:
    """
    Return normalised alert queue for the UI.
    - DATASET mode: returns up to MAX_UI_ALERTS real, normalised alerts.
    - DEMO mode:    returns EMPTY LIST.  The caller (views/alerts.py,
                    app.py) must surface the dataset-missing blocker
                    rather than silently substitute mock data.
    is_laundering is NEVER present in returned dicts.
    """
    raw = _load_dataset_alerts()
    if raw is None:
        return []          # caller must handle empty list explicitly
    return [_normalise(r) for r in raw]


def get_alert(alert_id: str) -> Optional[Dict[str, Any]]:
    """Return one normalised alert by ID, or None."""
    return next((a for a in get_alerts() if a["id"] == alert_id), None)


# ---------------------------------------------------------------------------
# Ground-truth access — OFFLINE EVALUATION ONLY
# ---------------------------------------------------------------------------

def get_alert_with_ground_truth(alert_id: str) -> Optional[Dict[str, Any]]:
    """
    Return the RAW alert dict INCLUDING is_laundering.
    FOR OFFLINE EVALUATION ONLY.
    MUST NOT be called from views/, integration/, or agent/.
    """
    raw = _load_dataset_alerts()
    if raw:
        return next((r for r in raw if r.get("alert_id") == alert_id), None)
    return None


def get_all_with_ground_truth() -> List[Dict[str, Any]]:
    """
    Return ALL raw alerts INCLUDING is_laundering.
    FOR OFFLINE EVALUATION ONLY.
    """
    raw = _load_dataset_alerts()
    return list(raw) if raw else []
