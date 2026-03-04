import os
from dotenv import load_dotenv
from scripts.schema import ACCOUNT_MEMO_TEMPLATE
from scripts.agent_schema import AGENT_TEMPLATE
from scripts.utils import ensure_dir, save_json, generate_account_id
from scripts.logger import log_event

from scripts.extractors.company import extract_company_name
from scripts.extractors.hours import extract_business_hours
from scripts.extractors.services import extract_services
from scripts.extractors.emergency import extract_emergency_definitions
from scripts.extractors.routing import extract_routing_rules
from scripts.extractors.integration import extract_integration_constraints
from scripts.extractors.unknowns import detect_unknowns, compute_confidence
from scripts.extractors.transfer import extract_transfer_rules
from scripts.extractors.flow_summary import (
    generate_office_hours_summary,
    generate_after_hours_summary
)
from scripts.llm_extractor import llm_extract
from scripts.llm_validator import validate_llm_output
from scripts.extractors.company import extract_company_name

load_dotenv()

DATASET_PATH = os.getenv("DATASET_PATH")
OUTPUT_PATH = os.getenv("OUTPUT_PATH")


def read_transcript(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_account_memo(text, account_id):
    memo = ACCOUNT_MEMO_TEMPLATE.copy()

    
    company = extract_company_name(text, account_id)
    if not company:
        company = "unknown_company"
    
    llm_data = validate_llm_output(llm_extract(text))
    # Apply LLM fields first
    for key, value in llm_data.items():
    
        if value is None:
            continue

        # nested dictionary merge
        if isinstance(value, dict) and key in memo:

            for sub_key, sub_value in value.items():

                if sub_value is None:
                    continue

                memo[key][sub_key] = sub_value

        else:
            memo[key] = value

    memo["company_name"] = company
    memo["account_id"] = account_id

    memo["business_hours"] = extract_business_hours(text)
    memo["services_supported"] = extract_services(text)
    memo["emergency_definition"] = extract_emergency_definitions(text)
    memo["emergency_routing_rules"] = extract_routing_rules(text)
    constraints = extract_integration_constraints(text)
    if constraints:
        memo["integration_constraints"] = constraints
    else:
        memo["integration_constraints"] = []
    if not memo["call_transfer_rules"]["timeout_seconds"]:
        memo["call_transfer_rules"] = extract_transfer_rules(text)

    memo["questions_or_unknowns"] = detect_unknowns(memo, stage="demo")
    memo["confidence_level"] = compute_confidence(memo)

    memo["notes"] = "Generated from demo transcript (v1)."

    memo["office_hours_flow_summary"] = generate_office_hours_summary(memo)
    memo["after_hours_flow_summary"] = generate_after_hours_summary(memo)

    return memo


def build_agent_spec(memo):
    agent = AGENT_TEMPLATE.copy()

    agent["agent_name"] = f"{memo['company_name']} - Clara v1"
    agent["variables"]["timezone"] = memo["business_hours"]["timezone"]
    agent["variables"]["business_hours"] = memo["business_hours"]
    agent["variables"]["office_address"] = memo["office_address"]
    agent["variables"]["emergency_routing"] = memo["emergency_definition"]

    agent["system_prompt"] = f"""
    You are Clara, the AI call agent for {memo['company_name']}.

    GENERAL RULES:
    - Be professional, calm, and concise.
    - Only collect information required for routing or dispatch.
    - Never invent business rules.
    - Never mention internal systems, APIs, or function calls.
    - If configuration is unclear, default to safe follow-up handling.

    --------------------------
    BUSINESS HOURS FLOW
    --------------------------
    1. Greet the caller.
    2. Ask for the purpose of the call.
    3. Collect caller name.
    4. Collect caller phone number.
    5. Determine if issue is emergency or non-emergency.
    6. Route or transfer according to defined routing rules.
    7. If transfer fails:
    - Apologize.
    - Inform caller that dispatch will follow up shortly.
    8. Ask if they need anything else.
    9. Close the call politely.

    --------------------------
    AFTER HOURS FLOW
    --------------------------
    1. Greet the caller.
    2. Ask for the purpose of the call.
    3. Confirm whether the issue is an emergency.
    4. If emergency:
    - Immediately collect name.
    - Immediately collect phone number.
    - Immediately collect service address.
    - Attempt transfer to emergency contact.
    - If transfer fails:
        - Apologize.
        - Assure rapid follow-up.
    5. If NOT emergency:
    - Collect name.
    - Collect phone number.
    - Briefly collect issue summary.
    - Inform caller team will follow up during business hours.
    6. Ask if they need anything else.
    7. Close politely.
    """

    agent["call_transfer_protocol"] = "Attempt transfer if specified."
    agent["transfer_failure_protocol"] = "Apologize and assure follow-up."
    agent["version"] = "v1"

    return agent


def process_demo_file(file_path):
    text = open(file_path, encoding="utf-8").read()
    account_id = os.path.basename(file_path).replace("_demo.txt", "")
    memo = build_account_memo(text, account_id)
    agent = build_agent_spec(memo)

    account_folder = os.path.join(OUTPUT_PATH, memo["account_id"], "v1")

    if os.path.exists(os.path.join(account_folder, "memo.json")):
        log_event("DEMO_V1", f"v1 already exists for {memo['account_id']} — skipped")
        return

    ensure_dir(account_folder)

    save_json(os.path.join(account_folder, "memo.json"), memo)
    save_json(os.path.join(account_folder, "agent_spec.json"), agent)

    log_event("DEMO_V1", f"Generated v1 for {memo['account_id']}")


if __name__ == "__main__":
    demo_folder = os.path.join(DATASET_PATH, "demo")

    for file in os.listdir(demo_folder):
        if file.endswith(".txt"):
            process_demo_file(os.path.join(demo_folder, file))