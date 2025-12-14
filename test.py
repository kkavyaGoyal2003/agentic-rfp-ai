from agents.sales_agent import run_sales_agent
from agents.main_agent.src.load_pdf import load_rfp_pdf
from agents.main_agent.src.summary import extract_role_relevant_text

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

# Step 3: Extract Technical & Testing Information
relevant_text = extract_role_relevant_text(pdf_data["full_text"])

print("\n--- Technical Information (for Technical Agent) ---")
for line in relevant_text["technical_text"]:
    print(line)

print("\n--- Testing & Acceptance Information (for Pricing Agent) ---")
for line in relevant_text["testing_text"]:
    print(line)
