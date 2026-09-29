"""
Singleton Hindsight client with graceful cleanup.
The Hindsight library uses aiohttp internally even for its sync API,
so an unclosed-session warning appears at process exit.
We register an atexit handler to call client.close() which suppresses it.
"""
import atexit
import logging
from memory.config import config
from hindsight_client import Hindsight

log = logging.getLogger(__name__)

_client: Hindsight | None = None


def get_hindsight_client() -> Hindsight:
    global _client
    if _client is None:
        _client = Hindsight(
            base_url=config.HINDSIGHT_BASE_URL,
            api_key=config.HINDSIGHT_API_KEY,
        )
        atexit.register(_cleanup)
    return _client


def _cleanup():
    """Close the HTTP session on process exit to suppress aiohttp warnings."""
    global _client
    if _client is not None:
        try:
            _client.close()
        except Exception:
            pass
        _client = None
