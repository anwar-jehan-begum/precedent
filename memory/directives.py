import time
from typing import Dict, Any, List
from memory.hindsight_client import get_hindsight_client
from memory.config import config

DIRECTIVES = [
    "Treat this system as analyst decision support, not as a final determination of money laundering.",
    "Do not invent customer history, analyst decisions, precedent cases, evidence, or outcomes.",
    "Distinguish historical analyst decisions from objective facts.",
    "When evidence is insufficient, explicitly state that the evidence is insufficient.",
    "Use retrieved historical evidence when forming reflections.",
    "Do not conceal uncertainty."
]

def setup_directives() -> Dict[str, Any]:
    """Configure directives in Hindsight bank."""
    client = get_hindsight_client()
    results = []
    
    try:
        existing_res = client.list_directives(bank_id=config.HINDSIGHT_BANK_ID)
        existing_directives = getattr(existing_res, "directives", []) or []
        existing_names = [getattr(d, "name", "") for d in existing_directives]
    except Exception as e:
        return {"success": False, "error": str(e)}

    for i, directive in enumerate(DIRECTIVES):
        name = f"aml-directive-{i+1}"
        if name in existing_names:
            results.append({"directive": directive, "status": "already_exists"})
            continue
            
        try:
            res = client.create_directive(
                bank_id=config.HINDSIGHT_BANK_ID,
                name=name,
                content=directive
            )
            results.append({"directive": directive, "status": "created"})
        except Exception as e:
            results.append({"directive": directive, "status": f"failed: {e}"})
            
    return {"success": True, "results": results}

def get_directives() -> Dict[str, Any]:
    """Get currently configured directives."""
    client = get_hindsight_client()
    try:
        directives = client.list_directives(bank_id=config.HINDSIGHT_BANK_ID)
        return {"success": True, "directives": directives}
    except Exception as e:
        return {"success": False, "error": str(e)}
