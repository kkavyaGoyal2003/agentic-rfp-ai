from typing import List, Dict
import csv
import os


def build_product_table(technical_text: List[str]) -> List[Dict]:
    """
    Builds a structured product table from extracted technical text.

    - Each product is grouped based on section headers (e.g., 4.1, 4.2, Item 1, Item 2)
    - Extracts only common, high-signal attributes
    - Preserves raw technical text for downstream resolution
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

        if not clean_line:
            continue

        # Detect new product section headers
        # Examples: "4.1 Instrumentation Cable", "4.2 33 kV XLPE Cable", "Item 1"
        header_token = clean_line.split()[0].replace(".", "")
        if header_token.isdigit() or clean_line.lower().startswith("item"):
            finalize_current_product()
            current_block.append(clean_line)
            continue

        current_block.append(clean_line)

        # Rule-based attribute extraction (INTENTIONALLY LIMITED)
        if "Category" in clean_line:
            current_product["category"] = clean_line.split("Category")[-1].strip()

        elif "Cable Type" in clean_line:
            current_product["cable_type"] = clean_line.split("Cable Type")[-1].strip()

        elif "Armored" in clean_line or "Armoured" in clean_line:
            current_product["armored"] = clean_line.split()[-1].strip()

        elif "Conductor Material" in clean_line:
            current_product["conductor_material"] = clean_line.split("Conductor Material")[-1].strip()

        elif "Conductor Size" in clean_line:
            current_product["conductor_size"] = clean_line.split("Conductor Size")[-1].strip()

        elif "Insulation Material" in clean_line:
            current_product["insulation_material"] = clean_line.split("Insulation Material")[-1].strip()

        elif "Sheath Material" in clean_line:
            current_product["sheath_material"] = clean_line.split("Sheath Material")[-1].strip()

        elif "Voltage Rating" in clean_line or "Rated Voltage" in clean_line:
            current_product["voltage_rating"] = clean_line.split()[-2] + " " + clean_line.split()[-1]

        elif "Applicable Standards" in clean_line or "Standards" in clean_line:
            current_product["standards"] = clean_line.split("Standards")[-1].strip()

    # Final product flush
    finalize_current_product()

    return products


def export_product_table_to_csv(product_table: List[Dict], tender_reference: str):
    """
    Exports product table to CSV for demo / inspection.
    This is a Main Agent utility and NOT used by downstream agents.
    """

    if not product_table:
        return None

    output_dir = "data/outputs"
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(
        output_dir,
        f"rfp_products_{tender_reference}.csv"
    )

    # Keep CSV clean; raw_block is internal only
    fieldnames = [
        "rfp_item_id",
        "category",
        "cable_type",
        "armored",
        "conductor_material",
        "conductor_size",
        "insulation_material",
        "sheath_material",
        "voltage_rating",
        "standards"
    ]

    with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for product in product_table:
            writer.writerow({
                key: product.get(key, "")
                for key in fieldnames
            })

    return file_path
