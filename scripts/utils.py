import os
import json
from datetime import datetime

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    ensure_dir(os.path.dirname(path))
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def generate_account_id(company_name):
    return company_name.lower().replace(" ", "_")

def timestamp():
    return datetime.utcnow().isoformat()

def normalize_time(t):
    if not t:
        return ""

    t = t.lower().replace(" ", "")

    if "am" in t or "pm" in t:
        return t.upper()

    return t