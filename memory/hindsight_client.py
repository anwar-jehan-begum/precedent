from memory.config import config
from hindsight_client import Hindsight

_client = None

def get_hindsight_client() -> Hindsight:
    global _client
    if _client is None:
        _client = Hindsight(
            base_url=config.HINDSIGHT_BASE_URL,
            api_key=config.HINDSIGHT_API_KEY
        )
    return _client
