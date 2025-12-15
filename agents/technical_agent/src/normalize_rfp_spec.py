import re
from typing import List, Dict


def normalize_rfp_specs(
    product_table: List[Dict],
    technical_summary: str
) -> List[Dict]:
    """
    Normalize RFP product requirements into a strict,
    comparable schema aligned with OEM datasheets.

    Returns one normalized spec dict per RFP item.
    """

    normalized_items = []

    for item in product_table:
        spec = {
            "rfp_item_id": item.get("rfp_item_id"),
            "category": normalize_category(item.get("category")),  # CHANGED
            "cable_type": normalize_text(item.get("cable_type")),
            "armored": normalize_armored(item),  # CHANGED
            "conductor_material": normalize_material(item.get("conductor_material")),  # CHANGED
            "conductor_size": normalize_conductor_size(
                item.get("conductor_size")
            ),
            "voltage_rating_v": extract_voltage(item),
            "standards": normalize_standards(item),
            "raw_block": item.get("raw_block", [])
        }

        normalized_items.append(spec)

    return normalized_items


# --------------------------------------------------
# Helpers (deterministic, no AI)
# --------------------------------------------------

def normalize_text(value):
    if not value:
        return None
    return value.strip().lower()


def normalize_category(value):
    """Map RFP categories to standardized categories"""
    if not value:
        return None
    
    value = value.lower().strip()
    
    # Category mapping
    if "instrument" in value:
        return "instrument cable"
    elif "power" in value or "33 kv" in value.lower():
        return "power cable"
    elif "control" in value:
        return "control cable"
    elif "communication" in value:
        return "communication cable"
    elif "data" in value:
        return "data cable"
    elif "fiber" in value:
        return "fiber optic"
    else:
        return value


def normalize_armored(item: Dict):
    """Normalize armored to STRING 'Y' or 'N' to match SKU format"""
    raw = " ".join(item.get("raw_block", [])).lower()
    if "armored yes" in raw or "armoured yes" in raw:
        return "Y"  # CHANGED: Return string 'Y'
    if "armored no" in raw or "armoured no" in raw:
        return "N"  # CHANGED: Return string 'N'
    
    # Check for armored in cable type
    if "armored" in raw or "armoured" in raw:
        return "Y"  # CHANGED: Return string 'Y'
    
    return "N"  # CHANGED: Default to 'N'

def normalize_material(value):
    """Normalize conductor material"""
    if not value:
        return None
    
    value = value.lower().strip()
    
    # Material mapping
    if "copper" in value:
        return "copper"
    elif "aluminium" in value or "aluminum" in value:
        return "aluminium"
    elif "steel" in value:
        return "steel"
    else:
        return value


def extract_voltage(item: Dict):
    if "voltage_rating" in item:
        return normalize_voltage(item["voltage_rating"])

    raw = " ".join(item.get("raw_block", []))
    match = re.search(r"(\d+)\s*k?v", raw, re.IGNORECASE)
    if match:
        return normalize_voltage(match.group(1))
    return None


def normalize_voltage(value):
    value = str(value).lower()
    if "kv" in value:
        return int(float(value.replace("kv", "").strip()) * 1000)
    return int(re.sub(r"\D", "", value))


def normalize_conductor_size(value):
    if not value:
        return None
    value = value.lower().replace("sqmm", "").replace("mm²", "").strip()
    return value


def normalize_standards(item: Dict):
    raw = " ".join(item.get("raw_block", []))
    standards = []

    if "iec" in raw.lower():
        standards.append("IEC")
    if "is " in raw.lower():
        standards.append("IS")

    return list(set(standards)) if standards else None