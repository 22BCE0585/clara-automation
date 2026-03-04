def validate_llm_output(data):
    
    if not isinstance(data, dict):
        return {}

    allowed_keys = {
        "business_hours",
        "services_supported",
        "emergency_definition",
        "emergency_routing_rules",
        "non_emergency_routing_rules",
        "call_transfer_rules",
        "integration_constraints"
    }

    clean = {}

    for key in allowed_keys:
        if key in data and data[key] is not None:
            clean[key] = data[key]

    return clean