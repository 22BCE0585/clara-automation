def detect_unknowns(memo, stage="demo"):
    unknowns = []

    if not memo["business_hours"]["days"]:
        if stage == "demo":
            unknowns.append("Business hours not clearly discussed during demo.")
        else:
            unknowns.append("Business hours not confirmed during onboarding.")

    if not memo["emergency_definition"]:
        if stage == "demo":
            unknowns.append("Emergency definitions not clarified during demo.")
        else:
            unknowns.append("Emergency definitions not explicitly confirmed during onboarding.")

    if not memo["services_supported"]:
        unknowns.append("Services supported not clearly identified.")

    return unknowns


def compute_confidence(memo):
    missing_count = len(memo["questions_or_unknowns"])

    if missing_count == 0:
        return "high"
    elif missing_count <= 2:
        return "medium"
    else:
        return "low"