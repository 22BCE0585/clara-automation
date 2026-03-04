def extract_emergency_definitions(text):
    triggers = []

    keywords = [
        "sprinkler leak",
        "water flowing",
        "fire alarm going off",
        "fire alarm triggered",
        "no power",
        "smoke",
        "urgent service"
    ]

    for k in keywords:
        if k.lower() in text.lower():
            triggers.append(k)

    return list(set(triggers))