import re

def normalize_time(t):
    return t.upper().replace(" ", "")

def extract_business_hours(text):
    result = {
        "days": [],
        "start": "",
        "end": "",
        "timezone": ""
    }

    # Detect common patterns like:
    # "Monday through Friday 6 AM to 6 PM"
    pattern = r"(Monday.*?Friday).*?(\d{1,2}(:\d{2})?\s?(AM|PM)).*?(\d{1,2}(:\d{2})?\s?(AM|PM))"

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        result["days"] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        result["start"] = normalize_time(match.group(2))
        result["end"] = normalize_time(match.group(5))

    # Detect timezone
    tz_match = re.search(r"(EST|CST|PST|MST|UTC)", text, re.IGNORECASE)
    if tz_match:
        result["timezone"] = tz_match.group(1).upper()

    return result