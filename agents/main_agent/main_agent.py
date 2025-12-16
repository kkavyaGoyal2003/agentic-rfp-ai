from agents.main_agent.pipeline import run_main_pipeline
from agents.technical_agent import run_technical_agent
from agents.pricing_agent import run_pricing_agent

from agents.main_agent.src.consolidate_response import consolidate_rfp_response
from agents.main_agent.src.generate_pdf import generate_rfp_response_pdf

# =====================================================
# UI ENTRY POINT — DRAFT PHASE (EDITABLE)
# =====================================================
def run_main_draft(rfp: dict) -> dict:
    """
    Generates editable Main Agent output.
    Used by UI.
    Does NOT call Technical or Pricing agents.
    """
    return run_main_pipeline(rfp)

# =====================================================
# LEGACY / AUTOMATION ENTRY POINT
# =====================================================
def run_main_agent(rfp: dict) -> dict:
    main_result = run_main_pipeline(rfp)

    technical_result = run_technical_agent(main_result)

    pricing_result = run_pricing_agent({
        **main_result,
        "technical_recommendations": technical_result["rfp_items"]
    })

    final_rfp_response = consolidate_rfp_response(
        main_result=main_result,
        technical_result=technical_result,
        pricing_result=pricing_result
    )

    pdf_path = (
        f"data/outputs/RFP_RESPONSE_"
        f"{main_result['rfp_metadata']['tender_reference']}.pdf"
    )

    generate_rfp_response_pdf(final_rfp_response, pdf_path)

    return {
        **main_result,
        "technical_recommendations": technical_result["rfp_items"],
        "pricing": pricing_result,
        "final_rfp_response": final_rfp_response,
        "final_pdf_path": pdf_path
    }
