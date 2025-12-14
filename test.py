from agents.sales_agent import run_sales_agent
from agents.main_agent.src.load_pdf import load_rfp_pdf

# Step 1: Run Sales Agent
rfp = run_sales_agent()
print("Sales Agent Output:")
print(rfp)

# Step 2: Run Main Agent (PDF Loader)
pdf_data = load_rfp_pdf(rfp["rfp_pdf_path"])

print("\nMain Agent Output:")
print(f"PDF Path: {pdf_data['rfp_pdf_path']}")
print(f"Pages Extracted: {pdf_data['num_pages']}")
print("\nText Preview:")
print(pdf_data["text_preview"])
