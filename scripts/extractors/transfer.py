import re

def extract_transfer_rules(text):
    rules = {
        "timeout_seconds": "",
        "retry_attempts": "",
        "failure_message": ""
    }

    lower_text = text.lower()

    timeout_match = re.search(r"(\d+)\s*seconds", lower_text)
    if timeout_match:
        rules["timeout_seconds"] = timeout_match.group(1)

    retry_match = re.search(r"(\d+)\s*(?:retries|attempts)", lower_text)
    if retry_match:
        rules["retry_attempts"] = retry_match.group(1)

    if "if transfer fails" in lower_text:
        rules["failure_message"] = "Assure caller follow-up"

    return rules