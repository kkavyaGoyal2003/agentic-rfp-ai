from typing import List, Dict


def build_product_table(technical_text: List[str]) -> List[Dict]:
    """
    Builds a structured product table from extracted technical text.
    Each product is grouped based on section headers (e.g., 4.1, 4.2).
    """

    products = []
    current_product = {}
    current_block = []
    item_id = 1

    def finalize_current_product():
        nonlocal item_id, current_product, current_block
        if current_product:
            current_product["rfp_item_id"] = item_id
            current_product["raw_block"] = current_block
            products.append(current_product)
            item_id += 1
        current_product = {}
        current_block = []

    for line in technical_text:
        clean_line = line.strip()

        # Detect new product section (e.g., 4.1 Instrumentation Cable)
        if clean_line[:3].replace(".", "").isdigit():
            finalize_current_product()
            current_block.append(clean_line)
            continue

        current_block.append(clean_line)

        # Attribute extraction (rule-based)
        if "Category" in clean_line:
            current_product["category"] = clean_line.split("Category")[-1].strip()
        elif "Cable Type" in clean_line:
            current_product["cable_type"] = clean_line.split("Cable Type")[-1].strip()
        elif "Armored" in clean_line:
            current_product["armored"] = clean_line.split("Armored")[-1].strip()
        elif "Conductor Material" in clean_line:
            current_product["conductor_material"] = clean_line.split("Conductor Material")[-1].strip()
        elif "Conductor Size" in clean_line:
            current_product["conductor_size"] = clean_line.split("Conductor Size")[-1].strip()
        elif "Insulation Material" in clean_line:
            current_product["insulation_material"] = clean_line.split("Insulation Material")[-1].strip()
        elif "Sheath Material" in clean_line:
            current_product["sheath_material"] = clean_line.split("Sheath Material")[-1].strip()
        elif "Voltage Rating" in clean_line:
            current_product["voltage_rating"] = clean_line.split("Voltage Rating")[-1].strip()
        elif "Applicable Standards" in clean_line:
            current_product["standards"] = clean_line.split("Applicable Standards")[-1].strip()

    # Final product
    finalize_current_product()

    return products
