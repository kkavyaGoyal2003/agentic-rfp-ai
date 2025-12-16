from agents.technical_agent.src.validate_input import validate_technical_input
from agents.technical_agent.src.load_oem import load_oem_products
from agents.technical_agent.src.normalize_specs import normalize_spec_block_llm
from agents.technical_agent.src.select_top_oem import select_top_oem_products
from agents.technical_agent.src.normalize_oem import normalize_oem_product
from core.llm.ollama_client import OllamaLLM

OEM_CSV_PATH = "data/oem_products.csv"


def run_technical_pipeline(main_result: dict) -> dict:

    # Step 1: Validate
    rfp_products = validate_technical_input(main_result)
    # Re-index RFP items sequentially (1, 2, ...)
    for idx, product in enumerate(rfp_products, start=1):
        product["rfp_item_id"] = idx


    # Step 2: Load OEM
    raw_oem_products = load_oem_products(OEM_CSV_PATH)
    oem_products = [normalize_oem_product(oem) for oem in raw_oem_products]


    # Step 3: Normalize (AI)
    llm = OllamaLLM(model="llama3.2")
    normalized_products = []

    for product in rfp_products:
        raw_text = "\n".join(product.get("raw_block", []))
        normalized = normalize_spec_block_llm(llm, raw_text)

        normalized = normalize_spec_block_llm(llm, raw_text)
        
        if not normalized or not isinstance(normalized, dict):
            normalized = {}

        normalized_products.append({
            "rfp_item_id": product.get("rfp_item_id"),
            "category": product.get("category"),
            "normalized_specs": normalized,
            "raw_product": product
        })

    # Step 4: Match & Rank OEMs
    recommendations = []

    for rfp in normalized_products:
        top_oems = select_top_oem_products(rfp, oem_products)

        recommendations.append({
            "rfp_item_id": rfp["rfp_item_id"],
            "category": rfp["category"],
            "top_oem_recommendations": top_oems
        })

    return {
        "status": "Technical Agent Step 4 completed",
        "rfp_items": recommendations
    }
