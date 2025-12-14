from typing import Dict, List


def extract_role_relevant_text(full_text: str) -> Dict[str, List[str]]:
    """
    Extracts ONLY:
    1. Technical-related text (for Technical Agent)
    2. Testing & acceptance-related text (for Pricing Agent)

    All other content is ignored.
    """

    lines = full_text.splitlines()

    technical_text = []
    testing_text = []

    technical_keywords = [
        "scope", "cable", "wire", "voltage", "kv",
        "conductor", "insulation", "xlpe", "pvc",
        "armour", "armored", "construction",
        "standard", "iec", "is ", "ieee"
    ]

    testing_keywords = [
        "test", "testing", "inspection",
        "acceptance", "routine test",
        "type test", "site test", "commissioning"
    ]

    exclude_keywords = [
        "price", "commercial", "emd", "bid security",
        "payment", "delivery", "penalty",
        "liquidated", "eligibility",
        "turnover", "experience"
    ]

    for line in lines:
        clean_line = line.strip()
        lower_line = clean_line.lower()

        if not clean_line:
            continue

        # Ignore clearly non-relevant sections
        if any(k in lower_line for k in exclude_keywords):
            continue

        # Testing & acceptance (goes to pricing agent later)
        if any(k in lower_line for k in testing_keywords):
            testing_text.append(clean_line)
            continue

        # Technical requirements (goes to technical agent later)
        if any(k in lower_line for k in technical_keywords):
            technical_text.append(clean_line)

    return {
        "technical_text": technical_text,
        "testing_text": testing_text
    }
