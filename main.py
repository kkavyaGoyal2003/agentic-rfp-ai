from agents.sales_agent import run_sales_agent
from agents.main_agent.main_agent import run_main_draft
from agents.technical_agent import run_technical_agent
from agents.pricing_agent import run_pricing_agent

from agents.main_agent.src.consolidate_response import consolidate_rfp_response
from agents.main_agent.src.generate_pdf import generate_rfp_response_pdf

def main():
    # ------------------------------------------------------
    # Step 1: Run Sales Agent
    # ------------------------------------------------------
    print(">> Running Sales Agent...")

    rfp = None
    for event in run_sales_agent():
        if event.get("type") == "FINAL_RESULT":
            rfp = event["data"]["selected_rfp"]

    print(">> Sales Agent completed.")
    print("✔ Selected RFP:", rfp.get("tender_reference"))

    # ------------------------------------------------------
    # Step 2: Run Main Agent
    # ------------------------------------------------------
    print("\n>> Running Main Agent (Summarizing)")

    main_result = run_main_draft(rfp)
    print("✔ Main Agent Summarized Successfully! - Data sent to Technical Agent.")

    # ------------------------------------------------------
    # Step 3: Run Technical Agent
    # ------------------------------------------------------
    print("\n>> Running Technical Agent")
    technical_result = run_technical_agent(main_result)
    print("✔ Technical Agent - Output sent to Main Agent.")

    # ------------------------------------------------------
    # Step 4: Run Pricing Agent
    # ------------------------------------------------------
    print("\n>> Running Pricing Agent")
    pricing_result = run_pricing_agent({
        **main_result,
        "technical_recommendations": technical_result["rfp_items"]
    })
    print("✔ Pricing Agent - Output sent to Main Agent.")

    # ------------------------------------------------------
    # Step 4: Generate Final Report
    # ------------------------------------------------------
    print("\n>> Running Main Agent (Generating Report)")
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
    print("✔ Main Agent - Report saved Successfully.")
    
    return {
        **main_result,
        "technical_recommendations": technical_result["rfp_items"],
        "pricing": pricing_result,
        "final_rfp_response": final_rfp_response,
        "final_pdf_path": pdf_path
    }
    
if __name__ == "__main__":
    main()

