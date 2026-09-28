import time
from memory.hindsight_client import get_hindsight_client
from memory.config import config

def check_hindsight_configuration():
    if not config.HINDSIGHT_API_KEY:
        return {
            "ok": False,
            "bank_id": config.HINDSIGHT_BANK_ID,
            "message": "HINDSIGHT_API_KEY is not set.",
            "latency_ms": 0
        }
    
    start_time = time.time()
    try:
        client = get_hindsight_client()
        # Verify bank is reachable and config is valid
        client.get_bank_config(config.HINDSIGHT_BANK_ID)
        
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "ok": True,
            "bank_id": config.HINDSIGHT_BANK_ID,
            "message": "Configuration is healthy and bank is reachable.",
            "latency_ms": latency_ms
        }
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "ok": False,
            "bank_id": config.HINDSIGHT_BANK_ID,
            "message": f"Connection failed: {str(e)}",
            "latency_ms": latency_ms
        }
