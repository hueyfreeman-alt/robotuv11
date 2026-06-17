import os
import logging

logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("TOKEN environment variable is required but not set")

_admin_id_raw = os.getenv("ADMIN_ID", "0")
try:
    ADMIN_ID = int(_admin_id_raw)
except ValueError:
    logger.error("ADMIN_ID must be an integer, got: %r. Defaulting to 0.", _admin_id_raw)
    ADMIN_ID = 0
