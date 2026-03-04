import os
import json
from datetime import datetime

LOG_FILE = "logs/pipeline.log"

def log_event(stage, message, level="INFO"):
    os.makedirs("logs", exist_ok=True)

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "stage": stage,
        "message": message
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")