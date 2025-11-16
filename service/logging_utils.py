# service/logging_utils.py
import logging
import json
from datetime import datetime

logger = logging.getLogger("timeseries_service")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')  # raw JSON in message
handler.setFormatter(formatter)
logger.addHandler(handler)

def log_event(event: str, job_id: str, **kwargs):
    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": event,
        "job_id": job_id,
        **kwargs,
    }
    logger.info(json.dumps(payload))
