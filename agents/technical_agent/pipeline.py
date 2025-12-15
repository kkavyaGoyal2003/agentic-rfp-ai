import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

from agents.technical_agent.src.load_data import load_oem_datasheet
from agents.technical_agent.src.normalize_rfp_spec import normalize_rfp_specs
from agents.technical_agent.src.filter_compliant_skus import filter_compliant_skus


def run_technical_pipeline(main_agent_output: dict) -> dict:
    """
    Core pipeline for Technical Agent.

    Receives structured RFP understanding from Main Agent and
    performs OEM SKU matching and recommendation.

    This pipeline will be incrementally implemented.
    """

    if not main_agent_output:
        raise ValueError("Invalid input to Technical Agent")

    product_table = main_agent_output.get("product_table")
    technical_summary = main_agent_output.get("technical_summary")

    if not product_table or not technical_summary:
        raise ValueError(
            "Technical Agent requires product_table and technical_summary"
        )

    # --------------------------------------------------
    # Step 1: Load OEM product datasheets
    # --------------------------------------------------
    datasheets = load_oem_datasheet()

    # --------------------------------------------------
    # Step 2: Normalize RFP specs
    # --------------------------------------------------
    rfp_specs = normalize_rfp_specs(product_table, technical_summary)

    rfp_results = []

    for rfp_item in rfp_specs:
        compliant, rejected = filter_compliant_skus(rfp_item, datasheets)

        rfp_results.append({
            "rfp_item_id": rfp_item["rfp_item_id"],
            "compliant_skus": [sku["sku"] for sku in compliant],
            "rejected_count": len(rejected)
        })

    return {
        "rfp_items": rfp_results,
        "status": "Technical Agent hard-gate matching completed"
    }
