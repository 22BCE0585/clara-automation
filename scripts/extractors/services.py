def extract_services(text):
    keywords = [
        "sprinkler",
        "fire alarm",
        "hvac",
        "electrical",
        "extinguisher",
        "inspection"
    ]

    services = []

    for keyword in keywords:
        if keyword.lower() in text.lower():
            services.append(keyword)

    return list(set(services))