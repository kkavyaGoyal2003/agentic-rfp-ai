from agents.sales_agent import run_sales_agent
from agents.main_agent.src.load_pdf import load_rfp_pdf
from agents.main_agent.src.summary import extract_role_relevant_text
from agents.main_agent.src.parse import (
    build_product_table,
    export_product_table_to_csv
)

print("\n================ MAIN AGENT TEST START ================\n")


# Step 1: Run Sales Agent

rfp = run_sales_agent()
print("Sales Agent Output:")
print(rfp)

# Safety check
if not rfp or "rfp_pdf_path" not in rfp:
    raise ValueError("Sales Agent did not return valid RFP data")


# Step 2: Load RFP PDF and extract text

pdf_data = load_rfp_pdf(rfp["rfp_pdf_path"])

print("\nMain Agent Output:")
print(f"PDF Path        : {pdf_data['rfp_pdf_path']}")
print(f"Pages Extracted : {pdf_data['num_pages']}")

print("\nText Preview:")
print(pdf_data["text_preview"])


# Step 3: Extract Technical & Testing Information

relevant_text = extract_role_relevant_text(pdf_data["full_text"])

print("\n--- Technical Information (for Technical Agent) ---")
if relevant_text["technical_text"]:
    for line in relevant_text["technical_text"]:
        print(line)
else:
    print("No technical information found.")

print("\n--- Testing & Acceptance Information (for Pricing Agent) ---")
if relevant_text["testing_text"]:
    for line in relevant_text["testing_text"]:
        print(line)
else:
    print("No testing / acceptance information found.")


# Step 4: Build Product Table from Technical Information

product_table = build_product_table(relevant_text["technical_text"])

print("\n--- Product Table (Structured Output) ---")
if product_table:
    for product in product_table:
        print(product)
else:
    print("No products could be structured from technical text.")

# Step 5: Export Product Table to CSV (Main Agent utility)

csv_path = export_product_table_to_csv(
    product_table,
    rfp["tender_reference"]
)

print("\n--- CSV Export ---")
if csv_path:
    print(f"CSV successfully generated at: {csv_path}")
else:
    print("CSV not generated (no product data).")

print("\n================ MAIN AGENT TEST END =================\n")
