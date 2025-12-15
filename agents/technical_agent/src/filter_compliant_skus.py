from typing import Dict, List, Tuple
import re


def normalize_yes_no(v):
    """Normalize Yes/No to STRING 'Y' or 'N' for consistent comparison"""
    if v is None:
        return None
    
    # If already 'Y' or 'N', return as is (case-insensitive)
    if isinstance(v, str):
        v_upper = v.strip().upper()
        if v_upper in ['Y', 'N']:
            return v_upper
    
    # Convert boolean
    if isinstance(v, bool):
        return 'Y' if v else 'N'
    
    # Convert other string values
    v_str = str(v).strip().lower()
    if v_str in {"y", "yes", "true", "1"}:
        return 'Y'
    elif v_str in {"n", "no", "false", "0"}:
        return 'N'
    
    return None

def extract_area_mm2(value: str) -> float:
    """Extract conductor area in mm² from various formats"""
    if not value:
        return 0.0
    
    try:
        # If it's already a number
        if isinstance(value, (int, float)):
            return float(value)
        
        v = str(value).lower().strip()
        
        # Match explicit mm² or sqmm
        m = re.search(r"([\d.]+)\s*(?:mm²|sqmm|mm2|sq\.?)?", v)
        if m:
            return float(m.group(1))
        
        # Match AWG (common in cables)
        m = re.search(r"(\d+)\s*awg", v)
        if m:
            awg = float(m.group(1))
            # Approximate AWG to mm² conversion
            return 0.012668 * (92 ** ((36 - awg) / 39))
        
        # Match "strands / dia" notation
        m = re.search(r"(\d+)\s*/\s*([\d.]+)", v)
        if m:
            strands = float(m.group(1))
            dia = float(m.group(2))
            # area = strands * π * (d/2)²
            return strands * 3.1416 * (dia / 2) ** 2
        
        # Try to extract any number
        m = re.search(r"([\d.]+)", v)
        if m:
            return float(m.group(1))
            
    except (ValueError, TypeError):
        pass
    
    return 0.0


def safe_float(v, default=0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def category_match(rfp_category: str, sku_category: str) -> bool:
    """Flexible category matching"""
    if not rfp_category or not sku_category:
        return True  # Don't reject if category is not specified
    
    rfp_cat = rfp_category.lower()
    sku_cat = sku_category.lower()
    
    # Mapping of category keywords
    category_keywords = {
        "instrument cable": ["instrument", "inst", "control"],
        "power cable": ["power", "pwr", "mv", "hv", "33kv"],
        "control cable": ["control", "ctl"],
        "communication cable": ["communication", "com", "telephone"],
        "data cable": ["data", "cat", "ethernet"],
        "fiber optic": ["fiber", "fibre", "optical"]
    }
    
    # Check if categories are related
    for main_cat, keywords in category_keywords.items():
        if rfp_cat == main_cat:
            # Check if any keyword matches SKU category
            for keyword in keywords:
                if keyword in sku_cat:
                    return True
    
    # Default: check if RFP category is in SKU category
    return rfp_cat in sku_cat or any(word in sku_cat for word in rfp_cat.split())


def filter_compliant_skus(
    rfp_item: Dict,
    datasheets: List[Dict]
) -> Tuple[List[Dict], List[Dict]]:

    compliant, rejected = [], []

    # --- RFP Specs ---
    rfp_category = (rfp_item.get("category") or "").lower()
    rfp_armored = normalize_yes_no(rfp_item.get("armored"))
    rfp_material = (rfp_item.get("conductor_material") or "").lower()
    rfp_voltage = safe_float(rfp_item.get("voltage_rating_v"))
    rfp_area = extract_area_mm2(rfp_item.get("conductor_size", ""))

    print(f"\n--- Filtering for RFP Item {rfp_item.get('rfp_item_id')} ---")
    print(f"RFP Specs: category={rfp_category}, armored={rfp_armored}, "
          f"material={rfp_material}, voltage={rfp_voltage}, area={rfp_area}")

    for sku in datasheets:
        reasons = []

        sku_category = (sku.get("category") or "").lower()
        sku_material = (sku.get("conductor_material") or "").lower()
        sku_voltage = safe_float(sku.get("voltage_rating_v"))
        sku_area = extract_area_mm2(sku.get("conductor_size", ""))

        # --- CATEGORY (Flexible matching) ---
        if rfp_category and not category_match(rfp_category, sku_category):
            reasons.append(f"category_mismatch: {rfp_category} vs {sku_category}")

        # --- ARMORED ---
        if rfp_armored is not None:
            sku_armored = normalize_yes_no(sku.get("armored"))
            if sku_armored != rfp_armored:
                reasons.append(f"armored_mismatch: {rfp_armored} vs {sku_armored}")

        # --- MATERIAL ---
        if rfp_material and rfp_material not in sku_material:
            # Check for material equivalences
            material_map = {
                "copper": ["copper", "cu", "atc"],
                "aluminium": ["aluminium", "aluminum", "al", "alum"],
                "steel": ["steel", "iron", "fe"]
            }
            
            if rfp_material in material_map:
                if not any(mat in sku_material for mat in material_map[rfp_material]):
                    reasons.append(f"material_mismatch: {rfp_material} vs {sku_material}")
            else:
                reasons.append(f"material_mismatch: {rfp_material} vs {sku_material}")

        # --- VOLTAGE (More flexible tolerance) ---
        if rfp_voltage > 0 and sku_voltage > 0:
            # For low voltage (≤1000V), allow ±20%
            # For medium/high voltage, allow ±10%
            tolerance = 0.2 if rfp_voltage <= 1000 else 0.1
            
            if sku_voltage < rfp_voltage * (1 - tolerance):
                reasons.append(f"voltage_too_low: {sku_voltage} < {rfp_voltage * (1 - tolerance)}")
            elif sku_voltage > rfp_voltage * (1 + tolerance):
                reasons.append(f"voltage_too_high: {sku_voltage} > {rfp_voltage * (1 + tolerance)}")

        # --- CONDUCTOR SIZE / AREA (±20% tolerance for now) ---
        if rfp_area > 0 and sku_area > 0:
            lower = rfp_area * 0.8  # 20% below
            upper = rfp_area * 1.2  # 20% above
            if not (lower <= sku_area <= upper):
                reasons.append(f"area_mismatch: {sku_area} not in range [{lower:.1f}, {upper:.1f}]")

        if reasons:
            rejected.append({"sku": sku.get("sku"), "reasons": reasons})
        else:
            compliant.append(sku)

    return compliant, rejected