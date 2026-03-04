import re

def extract_company_name(text, fallback):
    pattern = r"(?:this is|calling from|with)\s+([A-Z][A-Za-z0-9\s]+)"
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return match.group(1).strip()

    return fallback