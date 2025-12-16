from agents.sales_agent import run_sales_agent
from agents.main_agent import run_main_agent

print("\n================ AGENTIC RFP PIPELINE TEST START ================\n")

# ------------------------------------------------------
# Step 1: Run Sales Agent
# ------------------------------------------------------
print(">> Running Sales Agent...")

rfp = None
for event in run_sales_agent():
    if event.get("type") == "FINAL_RESULT":
        rfp = event["data"]["selected_rfp"]

print(">> Sales Agent completed.")

if not rfp:
    raise ValueError("❌ Sales Agent did not return an RFP")

print("✔ Selected RFP:", rfp.get("tender_reference"))

# ------------------------------------------------------
# Step 2: Run Main Agent (FULL PIPELINE)
# ------------------------------------------------------
print("\n>> Running Main Agent (Main → Technical → Pricing)...")

final_result = run_main_agent(rfp)

if not final_result:
    raise ValueError("❌ Main Agent failed")

print("✔ Main Agent completed")

# ------------------------------------------------------
# Step 3: Display Outputs
# ------------------------------------------------------
print("\n================ PIPELINE OUTPUTS ================\n")

print("RFP Reference :", final_result["rfp_metadata"]["tender_reference"])
print("PDF Path      :", final_result["pdf_info"]["path"])

# ---- Summaries ----
print("\n--- Technical Summary ---")
print(final_result["technical_summary"])

print("\n--- Pricing Summary ---")
print(final_result["pricing_summary"])

# ---- OEM + Pricing ----
print("\n--- OEM Recommendations & Pricing ---")

for row in final_result["pricing"]["materials"]:
    print(
        f"RFP Item: {row['rfp_item_id']} | "
        f"SKU: {row['sku']} | "
        f"Product: {row['product_name']} | "
        f"Unit Price: ₹{row['unit_price']}"
    )

print("\nTest / Service Costs:")
for test in final_result["pricing"]["tests"]:
    print(
        f"{test['test_name']} | "
        f"Applicable To: {test['applicable_to']} | "
        f"Cost: ₹{test['price']}"
    )

print("\nTotals:")
print("Material Cost :", final_result["pricing"]["total_material_cost"])
print("Test Cost     :", final_result["pricing"]["total_test_cost"])
print("Grand Total   :", final_result["pricing"]["grand_total"])
print("pdf is downloaded")

print("\n================ TEST END =================\n")
