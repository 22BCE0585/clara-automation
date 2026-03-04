def generate_office_hours_summary(memo):
    summary = []

    summary.append("During business hours:")
    if memo["integration_constraints"]:
        summary.append("Integration constraints are enforced during job handling.")

    if memo["emergency_routing_rules"]["transfer_required"]:
        summary.append("Emergency calls are transferred to "
                    f"{memo['emergency_routing_rules']['transfer_target'] or 'designated contact'}.")

    if memo["call_transfer_rules"]["timeout_seconds"]:
        summary.append(f"Transfer timeout set to {memo['call_transfer_rules']['timeout_seconds']} seconds.")

    summary.append("Non-emergency calls are collected and routed appropriately.")

    return " ".join(summary)


def generate_after_hours_summary(memo):
    summary = []

    summary.append("After hours handling:")
    if memo["integration_constraints"]:
        summary.append("System integration rules apply to after-hours job handling.")

    if memo["emergency_routing_rules"]["transfer_required"]:
        summary.append("Emergency calls trigger immediate transfer attempt.")

    summary.append("Non-emergency calls are collected and scheduled for follow-up during business hours.")

    return " ".join(summary)