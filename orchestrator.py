from agents.sales_agent import run_sales_agent
from agents.main_agent.main_agent import run_main_draft
from agents.technical_agent import run_technical_agent
from agents.pricing_agent import run_pricing_agent

from agents.main_agent.src.consolidate_response import consolidate_rfp_response
from agents.main_agent.src.generate_pdf import generate_rfp_response_pdf


def run_full_rfp_pipeline(urls=None):
    """
    UI-friendly orchestration pipeline with progress tracking.
    
    Yields progress events for live UI updates.
    Acts as the MAIN HUB.
    
    Enhanced with:
    - Progress percentages (0-100%)
    - Rich intermediate data for UI visualization
    - Thread-safe event structure
    """
    
    total_steps = 5  # Sales, Main Draft, Technical, Pricing, Main Final
    current_progress = 0
    step_progress = 100 // total_steps  # 20% per major step

    # ------------------------------------------------------
    # STEP 1: SALES AGENT (0-20%)
    # ------------------------------------------------------
    current_progress = 0
    yield {
        "step": "SALES_AGENT",
        "status": "STARTED",
        "message": "Scanning RFP sources...",
        "progress": current_progress,
        "agent_data": {"rfps_scanned": 0, "eligible_rfps": 0}
    }

    selected_rfp = None
    eligible_rfps = []
    rfp_count = 0
    
    for event in run_sales_agent(urls=urls):
        # Track intermediate data from sales agent
        if event.get("type") == "PROGRESS":
            rfp_count = event.get("data", {}).get("total_scanned", rfp_count)
            eligible_rfps = event.get("data", {}).get("eligible_rfps", eligible_rfps)
            
        yield {
            "step": "SALES_AGENT",
            "status": "PROGRESS",
            "event": event,
            "progress": min(15, current_progress + 5),  # Gradually increase to 15%
            "agent_data": {
                "rfps_scanned": rfp_count,
                "eligible_rfps": len(eligible_rfps),
                "current_url": event.get("data", {}).get("current_url", "")
            }
        }

        if event.get("type") == "FINAL_RESULT":
            selected_rfp = event["data"]["selected_rfp"]
            eligible_rfps = event["data"].get("eligible_rfps", [])

    if not selected_rfp:
        yield {
            "step": "SALES_AGENT",
            "status": "FAILED",
            "message": "No eligible RFP found",
            "progress": current_progress,
            "agent_data": {"rfps_scanned": rfp_count, "eligible_rfps": 0}
        }
        return

    current_progress = 20
    yield {
        "step": "SALES_AGENT",
        "status": "COMPLETED",
        "data": selected_rfp,
        "progress": current_progress,
        "agent_data": {
            "rfps_scanned": rfp_count,
            "eligible_rfps": len(eligible_rfps),
            "selected_rfp_title": selected_rfp.get("title", "Unknown"),
            "selected_rfp_org": selected_rfp.get("organization", "Unknown")
        }
    }

    # ------------------------------------------------------
    # STEP 2: MAIN AGENT - DRAFT (20-40%)
    # ------------------------------------------------------
    current_progress = 20
    yield {
        "step": "MAIN_AGENT",
        "status": "STARTED",
        "message": "Extracting RFP structure and summaries...",
        "progress": current_progress,
        "agent_data": {"sections_processed": 0, "total_sections": 0}
    }

    main_result = run_main_draft(selected_rfp)
    
    # Calculate sections processed
    sections_processed = 0
    total_sections = 0
    if "rfp_sections" in main_result:
        sections_processed = len(main_result["rfp_sections"])
    if "rfp_metadata" in main_result:
        # Estimate total sections based on structure
        total_sections = sections_processed + 3  # +3 for summary, requirements, timeline
    
    current_progress = 40
    yield {
        "step": "MAIN_AGENT",
        "status": "COMPLETED",
        "data": main_result,
        "progress": current_progress,
        "agent_data": {
            "sections_processed": sections_processed,
            "total_sections": total_sections,
            "tender_reference": main_result.get("rfp_metadata", {}).get("tender_reference", "N/A"),
            "organization": main_result.get("rfp_metadata", {}).get("organization", "N/A"),
            "executive_summary_length": len(main_result.get("executive_summary", "")) if "executive_summary" in main_result else 0
        }
    }

    # ------------------------------------------------------
    # STEP 3: TECHNICAL AGENT (40-60%)
    # ------------------------------------------------------
    current_progress = 40
    yield {
        "step": "TECHNICAL_AGENT",
        "status": "STARTED",
        "message": "Matching OEM products to RFP specs...",
        "progress": current_progress,
        "agent_data": {"items_processed": 0, "products_matched": 0}
    }

    technical_result = run_technical_agent(main_result)
    
    # Extract matching statistics
    items_processed = 0
    products_matched = 0
    if "rfp_items" in technical_result:
        items_processed = len(technical_result["rfp_items"])
        products_matched = sum(1 for item in technical_result["rfp_items"] 
                              if item.get("matched_products") and len(item["matched_products"]) > 0)
    
    current_progress = 60
    yield {
        "step": "TECHNICAL_AGENT",
        "status": "COMPLETED",
        "data": technical_result,
        "progress": current_progress,
        "agent_data": {
            "items_processed": items_processed,
            "products_matched": products_matched,
            "match_rate": f"{(products_matched/items_processed*100):.1f}%" if items_processed > 0 else "0%",
            "top_oem": max(
                [item.get("oem", "") for item in technical_result.get("rfp_items", []) if item.get("oem")],
                key=lambda x: [item.get("oem", "") for item in technical_result.get("rfp_items", [])].count(x),
                default="N/A"
            )
        }
    }

    # ------------------------------------------------------
    # STEP 4: PRICING AGENT (60-80%)
    # ------------------------------------------------------
    current_progress = 60
    yield {
        "step": "PRICING_AGENT",
        "status": "STARTED",
        "message": "Computing material and testing costs...",
        "progress": current_progress,
        "agent_data": {"items_priced": 0, "calculations_complete": False}
    }

    pricing_result = run_pricing_agent({
        **main_result,
        "technical_recommendations": technical_result["rfp_items"]
    })
    
    # Extract pricing statistics
    items_priced = len(pricing_result.get("item_costs", []))
    total_cost = pricing_result.get("total_cost", 0)
    material_cost = pricing_result.get("material_cost", 0)
    testing_cost = pricing_result.get("testing_cost", 0)
    
    current_progress = 80
    yield {
        "step": "PRICING_AGENT",
        "status": "COMPLETED",
        "data": pricing_result,
        "progress": current_progress,
        "agent_data": {
            "items_priced": items_priced,
            "calculations_complete": True,
            "total_cost": total_cost,
            "material_cost": material_cost,
            "testing_cost": testing_cost,
            "profit_margin": pricing_result.get("profit_margin", "N/A"),
            "final_price": pricing_result.get("final_price", 0)
        }
    }

    # ------------------------------------------------------
    # STEP 5: MAIN AGENT - FINAL REPORT (80-100%)
    # ------------------------------------------------------
    current_progress = 80
    yield {
        "step": "MAIN_AGENT",
        "status": "STARTED",
        "message": "Generating final RFP response...",
        "progress": current_progress,
        "agent_data": {"sections_generated": 0, "pdf_ready": False}
    }

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

    final_payload = {
        **main_result,
        "technical_recommendations": technical_result["rfp_items"],
        "pricing": pricing_result,
        "final_rfp_response": final_rfp_response,
        "final_pdf_path": pdf_path
    }
    
    # Count sections in final response
    sections_generated = len(final_rfp_response.get("sections", []))

    current_progress = 95
    yield {
        "step": "MAIN_AGENT",
        "status": "COMPLETED",
        "data": final_payload,
        "progress": current_progress,
        "agent_data": {
            "sections_generated": sections_generated,
            "pdf_ready": True,
            "pdf_path": pdf_path,
            "response_length": len(str(final_rfp_response))
        }
    }

    current_progress = 100
    yield {
        "step": "PIPELINE",
        "status": "DONE",
        "message": "RFP processing completed successfully",
        "data": final_payload,
        "progress": current_progress,
        "agent_data": {
            "total_rfps_scanned": rfp_count,
            "final_tender_reference": main_result.get("rfp_metadata", {}).get("tender_reference", "N/A"),
            "total_products_matched": products_matched,
            "final_price": pricing_result.get("final_price", 0),
            "pdf_download_ready": True,
            "processing_time_estimate": "Ready for download"
        }
    }