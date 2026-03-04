ACCOUNT_MEMO_TEMPLATE = {
    "account_id": "",
    "company_name": "",
    "business_hours": {
        "days": [],
        "start": "",
        "end": "",
        "timezone": ""
    },
    "office_address": "",
    "services_supported": [],
    "emergency_definition": [],
    "emergency_routing_rules": {
    "transfer_required": False,
    "transfer_target": "",
    "timeout_seconds": "",
    "fallback_action": ""
    },
    "non_emergency_routing_rules": {
        "collect_details": True,
        "followup_during_business_hours": True
    },
    "call_transfer_rules": {
        "timeout_seconds": "",
        "retry_attempts": "",
        "failure_message": ""
    },
    "integration_constraints": [
        {
            "system": "",
            "rule": "",
            "description": ""
        }
    ],
    "after_hours_flow_summary": "",
    "office_hours_flow_summary": "",
    "questions_or_unknowns": [],
    "notes": "",
    "confidence_level": ""
}