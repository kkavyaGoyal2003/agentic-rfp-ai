import pandas as pd

from agents.pricing_agent.src.validate_input import validate_pricing_input
from agents.pricing_agent.src.load_pricing import (
    load_product_prices,
    load_test_prices
)
from agents.pricing_agent.src.compute_pricing import compute_pricing

PRODUCT_PRICE_CSV = "data/product_pricing.csv"
TEST_PRICE_CSV = "data/test_pricing.csv"


def run_pricing_pipeline(main_result: dict) -> dict:
    """
    Pricing Agent Pipeline

    Flow:
    Main Agent
        ↓
    Technical recommendations + testing requirements
        ↓
    Pricing Agent
        ↓
    Consolidated pricing table
    """

    # --------------------------------------------------
    # Step 1: Validate input from Main Agent
    # --------------------------------------------------
    validated = validate_pricing_input(main_result)

    technical_recommendations = validated["technical_recommendations"]
    pricing_summary = validated["pricing_summary"]

    # --------------------------------------------------
    # Step 2: Load pricing repositories (CSV)
    # --------------------------------------------------
    product_prices = load_product_prices(PRODUCT_PRICE_CSV)
    test_prices = load_test_prices(TEST_PRICE_CSV)

    OEM_PRODUCT_CSV = "data/oem_products.csv"
    oem_df = pd.read_csv(OEM_PRODUCT_CSV)

    # --------------------------------------------------
    # Step 3: Compute pricing
    # --------------------------------------------------
    pricing_result = compute_pricing(
    technical_recommendations=technical_recommendations,
    pricing_summary=pricing_summary,   # ✅ CORRECT NAME
    product_prices=product_prices,
    test_prices=test_prices
    )

    #changes done in polishing added pandas above 
    enriched_materials = []

    for item in pricing_result["materials"]:
        sku = item.get("SKU") or item.get("sku")

        product_row = oem_df[oem_df["SKU"] == sku]

        if not product_row.empty:
            product = product_row.iloc[0]

            enriched_materials.append({
                **item,
                "Product_Name": product["Product_Name"],
                "Voltage_Rating_V": product["Voltage_Rating_V"],
                "Cable_Type": product["Cable_Type"],
                "Conductor_Size": product["Conductor_Size"],
                "Armored": product["Armored"]
            })
        else:
            enriched_materials.append(item)

    

    # --------------------------------------------------
    # Step 4: Build structured OEM recommendations
    # (THIS goes to Main Agent)
    # --------------------------------------------------

    oem_recommendations = []

    for idx, item in enumerate(enriched_materials, start=1):
        sku = item.get("SKU") or item.get("sku")
        unit_price = item.get("unit_price", 0)
        quantity = item.get("quantity", 1)

        oem_recommendations.append({
            "item_no": idx,
            "sku": sku,
            "product_name": item.get("Product_Name"),
            "quantity": quantity,
            "unit_price": unit_price,
            "total_price": unit_price * quantity,
            "why_recommended": build_reason(item)
        })

    #----------------------------------------------
    # --------------------------------------------------
    # Final output (to Main Agent)
    # --------------------------------------------------
    return {
        "status": "Pricing Agent completed",
        "oem_recommendations": oem_recommendations,   # ✅ NEW
        "materials": enriched_materials,
        "tests": pricing_result["tests"],
        "total_material_cost": pricing_result["total_material_cost"],
        "total_test_cost": pricing_result["total_test_cost"],
        "grand_total": pricing_result["grand_total"]
    }

def build_reason(product):
    reasons = []

    if product.get("Cable_Type"):
        reasons.append(f"{product['Cable_Type']} insulation as per RFP requirement")

    if product.get("Armored"):
        reasons.append("armored construction suitable for site conditions")

    if product.get("Voltage_Rating_V"):
        reasons.append(f"rated for {product['Voltage_Rating_V']} V applications")

    return ", ".join(reasons).capitalize()

