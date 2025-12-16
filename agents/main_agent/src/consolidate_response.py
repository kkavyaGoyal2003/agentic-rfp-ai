def consolidate_rfp_response(
    main_result: dict,
    technical_result: dict,
    pricing_result: dict
) -> dict:
    """
    Consolidates Technical and Pricing outputs into
    a single RFP-ready response structure.
    """

    consolidated_pricing_table = []

    for rec in pricing_result["oem_recommendations"]:
        consolidated_pricing_table.append({
            # Commercial identifiers
            "item_no": rec["item_no"],
            "sku": rec["sku"],
            "product_name": rec["product_name"],

            # Pricing details
            "quantity": rec["quantity"],
            "unit_price": rec["unit_price"],
            "total_price": rec["total_price"],

            # Compliance & presentation
            "compliance_status": "Compliant",
            "standards": rec.get("standards", "As per applicable IS / IEC standards"),
            "technical_highlights": rec["why_recommended"]
        })

    return {
        "rfp_reference": main_result["rfp_metadata"]["tender_reference"],

        # Main consolidated table for RFP response
        "consolidated_pricing_table": consolidated_pricing_table,

        # Testing & acceptance costs
        "tests": pricing_result["tests"],

        # Cost summary
        "totals": {
            "material_cost": pricing_result["total_material_cost"],
            "test_cost": pricing_result["total_test_cost"],
            "grand_total": pricing_result["grand_total"]
        }
    }
