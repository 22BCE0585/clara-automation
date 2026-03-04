import os
from dotenv import load_dotenv
from scripts.utils import load_json, save_json, ensure_dir
from scripts.schema import ACCOUNT_MEMO_TEMPLATE
from scripts.agent_schema import AGENT_TEMPLATE
from scripts.logger import log_event

from scripts.extractors.hours import extract_business_hours
from scripts.extractors.emergency import extract_emergency_definitions
from scripts.extractors.integration import extract_integration_constraints
from scripts.extractors.routing import extract_routing_rules
from scripts.extractors.unknowns import detect_unknowns, compute_confidence
from scripts.extractors.transfer import extract_transfer_rules
from scripts.extractors.flow_summary import (
    generate_office_hours_summary,
    generate_after_hours_summary
)

load_dotenv()

DATASET_PATH = os.getenv("DATASET_PATH")
OUTPUT_PATH = os.getenv("OUTPUT_PATH")

def generate_change_summary(diff):
    if not diff:
        return "No operational changes detected."

    operational_fields = {
        "business_hours",
        "emergency_routing_rules",
        "non_emergency_routing_rules",
        "call_transfer_rules",
        "integration_constraints"
    }

    metadata_fields = {
        "notes",
        "confidence_level",
        "questions_or_unknowns"
    }

    changed_keys = set(diff.keys())

    if changed_keys.issubset(metadata_fields):
        return "Onboarding updated metadata and clarification notes only. No operational routing changes detected."

    if "business_hours" in changed_keys:
        return "Business hours configuration was updated during onboarding."

    if "emergency_routing_rules" in changed_keys:
        return "Emergency routing rules were updated during onboarding."

    if "integration_constraints" in changed_keys:
        return "Integration constraints were modified during onboarding."

    if operational_fields.intersection(changed_keys):
        return "Operational configuration was updated during onboarding."

    return "Configuration updated during onboarding."

def simple_diff(old, new):
    changes = {}

    for key in new:
        if old.get(key) != new.get(key):
            changes[key] = {
                "old": old.get(key),
                "new": new.get(key)
            }

    return changes

def read_transcript(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def apply_patch(v1_memo, onboarding_text):
    v2_memo = v1_memo.copy()

    # Extract updated fields from onboarding
    updated_hours = extract_business_hours(onboarding_text)
    updated_emergency = extract_emergency_definitions(onboarding_text)
    updated_integration = extract_integration_constraints(onboarding_text)
    updated_routing = extract_routing_rules(onboarding_text)
    updated_transfer = extract_transfer_rules(onboarding_text)

    for key, value in updated_transfer.items():
        if value != "":
            v2_memo["call_transfer_rules"][key] = value

    # Apply only if explicitly present
    if updated_hours["days"]:
        v2_memo["business_hours"] = updated_hours

    if updated_emergency:
        v2_memo["emergency_definition"] = updated_emergency

    if updated_integration:
        v2_memo["integration_constraints"] = updated_integration

    if any(updated_routing.values()):
        for key, value in updated_routing.items():
            if value != "":
                v2_memo["emergency_routing_rules"][key] = value
    v2_memo["office_hours_flow_summary"] = generate_office_hours_summary(v2_memo)
    v2_memo["after_hours_flow_summary"] = generate_after_hours_summary(v2_memo)
    v2_memo["notes"] = "Updated from onboarding transcript (v2)."

    v2_memo["questions_or_unknowns"] = detect_unknowns(v2_memo, stage="onboarding")
    
    v2_memo["confidence_level"] = compute_confidence(v2_memo)

    return v2_memo


def generate_v2_agent(v2_memo):
    agent = AGENT_TEMPLATE.copy()

    agent["agent_name"] = f"{v2_memo['company_name']} - Clara v2"
    agent["variables"]["timezone"] = v2_memo["business_hours"]["timezone"]
    agent["variables"]["business_hours"] = v2_memo["business_hours"]
    agent["variables"]["office_address"] = v2_memo["office_address"]
    agent["variables"]["emergency_routing"] = v2_memo["emergency_definition"]

    agent["system_prompt"] = f"""
    You are Clara, the AI call agent for {v2_memo['company_name']}.

    You MUST follow confirmed onboarding configuration strictly.

    GENERAL RULES:
    - Only collect information necessary for routing and dispatch.
    - Do NOT ask unnecessary questions.
    - Do NOT invent policies.
    - Do NOT mention internal tools or integrations.

    ----------------------
    BUSINESS HOURS FLOW
    ----------------------
    1. Greet caller.
    2. Ask purpose of call.
    3. Collect caller name.
    4. Collect caller phone number.
    5. Classify issue based on confirmed emergency definitions.
    6. Route or transfer according to confirmed routing rules.
    7. If transfer fails:
    - Apologize.
    - Inform caller dispatch will follow up.
    8. Ask if anything else is needed.
    9. Close professionally.

    ----------------------
    AFTER HOURS FLOW
    ----------------------
    1. Greet caller.
    2. Ask purpose.
    3. Confirm emergency status.
    4. If emergency:
    - Collect name immediately.
    - Collect phone number immediately.
    - Collect service address immediately.
    - Attempt emergency transfer.
    - If transfer fails:
        - Apologize.
        - Assure urgent follow-up.
    5. If non-emergency:
    - Collect name.
    - Collect phone number.
    - Collect short issue description.
    - Inform caller follow-up will occur during business hours.
    6. Ask if anything else is needed.
    7. Close politely.
    """

    agent["call_transfer_protocol"] = "Follow confirmed onboarding routing rules."
    agent["transfer_failure_protocol"] = "Apologize and ensure dispatch follow-up."
    agent["version"] = "v2"

    return agent


def process_onboarding_file(file_path):
    onboarding_text = read_transcript(file_path)

    # Extract account_id from filename
    filename = os.path.basename(file_path)
    account_id = os.path.basename(file_path).replace("_onboarding.txt", "")

    v1_path = os.path.join(OUTPUT_PATH, account_id, "v1", "memo.json")

    if not os.path.exists(v1_path):
        print(f"v1 not found for {account_id}")
        return

    v1_memo = load_json(v1_path)

    v2_memo = apply_patch(v1_memo, onboarding_text)

    v2_folder = os.path.join(OUTPUT_PATH, account_id, "v2")

    if os.path.exists(os.path.join(v2_folder, "memo.json")):
        log_event("ONBOARDING_V2", f"v2 already exists for {account_id} — skipped")
        return

    ensure_dir(v2_folder)

    diff = simple_diff(v1_memo, v2_memo)

    summary_text = generate_change_summary(diff)

    change_summary = {
        "stage": "onboarding_update",
        "summary": summary_text,
        "changes_detected": list(diff.keys()),
        "details": diff
    }

    save_json(os.path.join(v2_folder, "memo.json"), v2_memo)
    save_json(os.path.join(v2_folder, "agent_spec.json"), generate_v2_agent(v2_memo))
    save_json(os.path.join(v2_folder, "changes.json"), change_summary)

    log_event("ONBOARDING_V2", f"Generated v2 for {account_id}")


if __name__ == "__main__":
    onboarding_folder = os.path.join(DATASET_PATH, "onboarding")

    for file in os.listdir(onboarding_folder):
        if file.endswith("_onboarding.txt"):
            process_onboarding_file(os.path.join(onboarding_folder, file))