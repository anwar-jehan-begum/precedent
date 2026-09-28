import time
from typing import Dict, Any
from memory.hindsight_client import get_hindsight_client
from memory.config import config
from memory.retain import retain_alert, retain_analyst_decision
from memory.memory_schema import HistoricalCase

DEMO_SEED_VERSION = "v2"

def has_been_seeded() -> bool:
    """Check if the seed has already been applied."""
    client = get_hindsight_client()
    try:
        response = client.recall(
            bank_id=config.HINDSIGHT_BANK_ID,
            query="seed_version_check",
            tags=[f"seed_version:{DEMO_SEED_VERSION}"]
        )
        if hasattr(response, "results") and len(response.results) > 0:
            return True
        return False
    except Exception:
        return False

def mark_seeded():
    """Mark the bank as seeded."""
    client = get_hindsight_client()
    client.retain(
        bank_id=config.HINDSIGHT_BANK_ID,
        content=f"System seeded with demo data version {DEMO_SEED_VERSION}",
        tags=[f"seed_version:{DEMO_SEED_VERSION}"]
    )

def seed_data() -> Dict[str, Any]:
    """Seed synthetic data into the memory."""
    if has_been_seeded():
        return {"success": True, "message": f"Already seeded with version {DEMO_SEED_VERSION}."}
        
    print("Starting data seeding...")
    
    # Meridian Imports - Initial Clear
    alert_1 = HistoricalCase(
        alert_id="AML-1001",
        customer_id="Meridian Imports",
        typology="Rapid Movement",
        amount=45000.0,
        transaction_pattern="Multiple quick transfers under reporting threshold",
        risk_indicators=["Velocity change"],
        timestamp="2026-03-14T10:30:00Z",
        analyst="A. Kumar",
        agent_recommendation="CLEAR",
        final_decision="CLEAR",
        override=False,
        analyst_reason="Consistent with established historical supplier payments.",
        outcome="Cleared"
    )
    retain_alert(alert_1)
    retain_analyst_decision(alert_1.model_dump(), "CLEAR", "CLEAR", "Consistent with established historical supplier payments.")
    
    # Meridian Imports - The Override
    alert_2 = HistoricalCase(
        alert_id="AML-1042",
        customer_id="Meridian Imports",
        typology="Rapid Movement",
        amount=52000.0,
        transaction_pattern="Multiple quick transfers to new counterparties",
        risk_indicators=["Velocity change", "New counterparty"],
        timestamp="2026-08-14T14:20:00Z",
        analyst="A. Kumar",
        agent_recommendation="CLEAR",
        final_decision="ESCALATE",
        override=True,
        analyst_reason="Recent behavioral change. Counterparties are new and unverified.",
        outcome="Pending Investigation"
    )
    retain_alert(alert_2)
    retain_analyst_decision(alert_2.model_dump(), "CLEAR", "ESCALATE", "Recent behavioral change. Counterparties are new and unverified.")
    
    # Nova Trading - Structuring and Inconsistency
    alert_3 = HistoricalCase(
        alert_id="AML-1020",
        customer_id="Nova Trading",
        typology="Structuring",
        amount=9500.0,
        transaction_pattern="Cash deposits just under 10k limit on consecutive days",
        risk_indicators=["Cash intensity", "Velocity"],
        timestamp="2026-07-20T09:15:00Z",
        analyst="J. Smith",
        agent_recommendation="ESCALATE",
        final_decision="ESCALATE",
        override=False,
        analyst_reason="Classic structuring behavior observed over 3 days.",
        outcome="Report Filed"
    )
    retain_alert(alert_3)
    retain_analyst_decision(alert_3.model_dump(), "ESCALATE", "ESCALATE", "Classic structuring behavior observed over 3 days.")
    
    # Nova Trading - Second Structuring Alert (Inconsistency demo: incorrectly cleared later)
    alert_4 = HistoricalCase(
        alert_id="AML-1088",
        customer_id="Nova Trading",
        typology="Structuring",
        amount=9800.0,
        transaction_pattern="Cash deposits just under 10k limit on consecutive days",
        risk_indicators=["Cash intensity"],
        timestamp="2026-09-02T11:00:00Z",
        analyst="M. Davis",
        agent_recommendation="ESCALATE",
        final_decision="CLEAR",
        override=True,
        analyst_reason="Looks like normal retail business revenue.",
        outcome="Cleared"
    )
    retain_alert(alert_4)
    retain_analyst_decision(alert_4.model_dump(), "ESCALATE", "CLEAR", "Looks like normal retail business revenue.")
    
    # Acme Retail - Synthetic PEP
    alert_5 = HistoricalCase(
        alert_id="AML-1099",
        customer_id="Acme Retail",
        typology="High Risk Geography",
        amount=150000.0,
        transaction_pattern="Large wire transfer to high risk jurisdiction",
        risk_indicators=["Geography", "PEP Match"],
        timestamp="2026-09-15T16:45:00Z",
        analyst="L. Chen",
        agent_recommendation="ESCALATE",
        final_decision="ESCALATE",
        override=False,
        analyst_reason="Beneficial owner matched on synthetic PEP list. Enhanced Due Diligence required.",
        outcome="EDD Triggered"
    )
    retain_alert(alert_5)
    retain_analyst_decision(alert_5.model_dump(), "ESCALATE", "ESCALATE", "Beneficial owner matched on synthetic PEP list. Enhanced Due Diligence required.")

    # Mark as completed
    mark_seeded()
    print(f"Seeding completed successfully (version {DEMO_SEED_VERSION}).")
    
    return {"success": True, "message": "Seeding completed successfully."}
    
if __name__ == "__main__":
    seed_data()
