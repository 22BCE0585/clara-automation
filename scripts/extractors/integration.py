import re

def extract_integration_constraints(text):
    constraints = []

    lower_text = text.lower()

    # Detect ServiceTrade
    if "servicetrade" in lower_text:
        system = "ServiceTrade"

        # Detect restrictions
        if "never create" in lower_text and "sprinkler" in lower_text:
            constraints.append({
                "system": system,
                "rule": "never_create_sprinkler_jobs",
                "description": "Do not create sprinkler jobs automatically in ServiceTrade."
            })

        elif "never create" in lower_text:
            constraints.append({
                "system": system,
                "rule": "restricted_job_creation",
                "description": "Certain job types must not be auto-created in ServiceTrade."
            })

        else:
            constraints.append({
                "system": system,
                "rule": "integration_present",
                "description": "ServiceTrade integration mentioned."
            })

    return constraints