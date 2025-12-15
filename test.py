from agents.sales_agent import run_sales_agent
from agents.main_agent import run_main_agent
from agents.technical_agent import run_technical_agent


print("\n================ MAIN AGENT TEST START ================\n")

# ------------------------------------------------------
# Step 1: Run Sales Agent
# ------------------------------------------------------
rfp = run_sales_agent()

if not rfp:
    raise ValueError("Sales Agent did not return an RFP")

<<<<<<< HEAD

=======
>>>>>>> 75f4f25f85f9df3ba6c585ff833efd005c8786fe
# ------------------------------------------------------
# Step 2: Run Main Agent
# ------------------------------------------------------
main_result = run_main_agent(rfp)

# ------------------------------------------------------
# Step 3: Run Technical Agent
# ------------------------------------------------------
technical_result = run_technical_agent(main_result)

# ------------------------------------------------------
# Step 4: Display Outputs (test-only)
# ------------------------------------------------------
print("RFP Reference    :", main_result["rfp_metadata"].get("tender_reference"))

print("\n--- Main Agent: Technical Summary ---")
print(main_result.get("technical_summary", "No technical summary generated"))

print("\n--- Main Agent: Pricing Summary ---")
print(main_result.get("pricing_summary", "No pricing summary generated"))

print("\n--- Technical Agent Output ---")
print(technical_result)

print("\n================ MAIN AGENT TEST END =================\n")
