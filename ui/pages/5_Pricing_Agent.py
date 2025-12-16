import streamlit as st
from agents.pricing_agent.pricing_agent import run_pricing_agent

st.set_page_config(page_title="Pricing Agent", layout="wide")
st.title("💰 Pricing Agent")

# -------------------------------
# GUARD: Must receive Main-to-Pricing output
# -------------------------------
if "main_to_pricing" not in st.session_state:
    st.info("Waiting for Main Agent to send pricing context.")
    st.stop()

main_result = st.session_state.main_to_pricing

st.subheader("📦 Input from Main Agent")
with st.expander("View Main + Technical Data"):
    st.json({
        "RFP Reference": main_result["rfp_metadata"].get("tender_reference"),
        "Product Table Items": len(main_result.get("product_table", [])),
        "Technical Recommendations": len(main_result.get("technical_recommendations", []))
    })

# -------------------------------
# RUN PRICING AGENT
# -------------------------------
if "pricing_result" not in st.session_state:
    if st.button("💰 Compute Pricing"):
        with st.spinner("Computing pricing for products and tests..."):
            pricing = run_pricing_agent(main_result)
            st.session_state.pricing_result = pricing

            # Send back to Main Agent
            st.session_state.main_with_pricing = {
                **main_result,
                "pricing": pricing
            }
            st.success("Pricing results sent back to Main Agent ✅")

# -------------------------------
# DISPLAY PRICING RESULTS
# -------------------------------
if "pricing_result" in st.session_state:
    pricing = st.session_state.pricing_result

    st.divider()
    st.subheader("✅ Pricing Computation Completed")

    st.markdown("### 🏷️ Materials")
    st.dataframe(pricing.get("materials", []), use_container_width=True)

    st.markdown("### 🧪 Tests")
    st.dataframe(pricing.get("tests", []), use_container_width=True)

    st.markdown("### 💵 Totals")
    st.json({
        "Total Material Cost": pricing.get("total_material_cost"),
        "Total Test Cost": pricing.get("total_test_cost"),
        "Grand Total": pricing.get("grand_total")
    })
