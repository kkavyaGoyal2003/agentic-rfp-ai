from agents.sales_agent import run_sales_agent
from agents.main_agent import run_main_agent
from agents.technical_agent import run_technical_agent


print("\n================ AGENTIC RFP PIPELINE TEST START ================\n")

# ------------------------------------------------------
# Step 1: Run Sales Agent
# ------------------------------------------------------
print(">> Running Sales Agent...")

rfp = None
for event in run_sales_agent():
    if event["type"] == "FINAL_RESULT":
        rfp = event["data"]["selected_rfp"]

print(">> Sales Agent completed.")
print(rfp)


if not rfp:
    raise ValueError("Sales Agent did not return an RFP")

print("✔ Selected RFP:", rfp.get("tender_reference"))


# ------------------------------------------------------
# Step 2: Run Main Agent
# ------------------------------------------------------
print("\n>> Running Main Agent...")
main_result = run_main_agent(rfp)

if not main_result:
    raise ValueError("Main Agent failed")

print("✔ Main Agent completed")


# ------------------------------------------------------
# Step 3: Run Technical Agent (Step 1 only for now)
# ------------------------------------------------------
print("\n>> Running Technical Agent (Step 1 – validation & OEM load)...")
technical_result = run_technical_agent(main_result)

print("✔ Technical Agent executed")


# ------------------------------------------------------
# Step 4: Display Outputs (TEST ONLY)
# ------------------------------------------------------
print("\n================ PIPELINE OUTPUTS ================\n")

# ---- RFP Info ----
print("RFP Reference :", main_result["rfp_metadata"].get("tender_reference"))
print("PDF Path      :", main_result["rfp_metadata"].get("rfp_pdf_path"))

# ---- Main Agent Summaries ----
print("\n--- Main Agent : Technical Summary ---")
print(main_result.get("technical_summary", "❌ No technical summary generated"))

print("\n--- Main Agent : Pricing Summary ---")
print(main_result.get("pricing_summary", "❌ No pricing summary generated"))

print("\n--- Main Agent : Product Table Path ---")
print(main_result.get("product_csv", "❌ No product CSV generated"))

# ---- Technical Agent Output ----
print("\n--- Technical Agent : OEM Recommendations ---")

for item in technical_result["rfp_items"]:
    print(f"\nRFP Item ID : {item['rfp_item_id']}")
    print(f"Category    : {item['category']}")
    print("Top 3 OEM Recommendations:")

    for idx, oem in enumerate(item["top_oem_recommendations"], start=1):
        print(f"  {idx}. SKU          : {oem['sku']}")
        print(f"     Product Name : {oem['product_name']}")
        print(f"     Match Score  : {oem['score']}%")


print("\n================ TEST END =================\n")
