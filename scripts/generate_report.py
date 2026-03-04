import os
import json

OUTPUT_DIR = "outputs/accounts"
REPORT_PATH = "outputs/report.json"


def generate_report():

    report = {
        "accounts_processed": 0,
        "v1_generated": 0,
        "v2_generated": 0,
        "unknown_fields_detected": 0,
        "confidence_levels": {}
    }

    if not os.path.exists(OUTPUT_DIR):
        return report

    for account in os.listdir(OUTPUT_DIR):

        report["accounts_processed"] += 1

        account_path = os.path.join(OUTPUT_DIR, account)

        v1_path = os.path.join(account_path, "v1", "memo.json")
        v2_path = os.path.join(account_path, "v2", "memo.json")

        if os.path.exists(v1_path):

            report["v1_generated"] += 1

            with open(v1_path) as f:
                memo = json.load(f)

                report["unknown_fields_detected"] += len(
                    memo.get("questions_or_unknowns", [])
                )

                confidence = memo.get("confidence_level", "unknown")

                report["confidence_levels"][confidence] = (
                    report["confidence_levels"].get(confidence, 0) + 1
                )

        if os.path.exists(v2_path):
            report["v2_generated"] += 1

    os.makedirs("outputs", exist_ok=True)

    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)

    print("Report generated at outputs/report.json")


if __name__ == "__main__":
    generate_report()