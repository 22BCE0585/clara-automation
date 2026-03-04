import re

def extract_routing_rules(text):
    routing = {
        "transfer_required": False,
        "transfer_target": "",
        "timeout_seconds": "",
        "fallback_action": ""
    }

    lower_text = text.lower()

    if "transfer" in lower_text:
        routing["transfer_required"] = True

    if "dispatch" in lower_text:
        routing["transfer_target"] = "dispatch"

    timeout_match = re.search(r"(\d+)\s*seconds", lower_text)
    if timeout_match:
        routing["timeout_seconds"] = timeout_match.group(1)

    if "supervisor" in lower_text:
        routing["fallback_action"] = "notify_supervisor"

    return routing