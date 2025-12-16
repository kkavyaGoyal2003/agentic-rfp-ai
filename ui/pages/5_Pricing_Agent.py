import streamlit as st
from agents.pricing_agent.pricing_agent import run_pricing_agent

st.set_page_config(page_title="Pricing Agent", layout="wide")
st.title("💰 Pricing Agent")
st.caption("Compute material, testing, and consolidated pricing for the selected RFP")

# ==================================================
# GUARD: Await Main Agent Pricing Context
# ==================================================
if "main_to_pricing" not in st.session_state:
    st.info("Waiting for Main Agent to send pricing context.")
    st.stop()

main_result = st.session_state.main_to_pricing

# ==================================================
# INPUT CONTEXT
# ==================================================
with st.container(border=True):
    st.subheader("📥 Input from Main Agent")

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "RFP Reference",
        main_result["rfp_metadata"].get("tender_reference", "—")
    )
    col2.metric(
        "Product Items",
        len(main_result.get("product_table", []))
    )
    col3.metric(
        "Technical Matches",
        len(main_result.get("technical_recommendations", []))
    )

    with st.expander("🔍 View Full Pricing Context"):
        st.json({
            "RFP Metadata": main_result["rfp_metadata"],
            "Product Table": main_result.get("product_table", []),
            "Technical Recommendations": main_result.get("technical_recommendations", [])
        })

# ==================================================
# STEP 1: Run Pricing Agent
# ==================================================
st.divider()
st.subheader("① Compute Pricing")

if "pricing_result" not in st.session_state:
    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button("💰 Compute Pricing", use_container_width=True):
            with st.spinner("Calculating material and testing costs..."):
                pricing = run_pricing_agent(main_result)
                st.session_state.pricing_result = pricing

                # Send back to Main Agent
                st.session_state.main_with_pricing = {
                    **main_result,
                    "pricing": pricing
                }

                st.success("Pricing results computed and sent to Main Agent ✅")

    with col2:
        st.info(
            "Pricing Agent will:\n"
            "- Aggregate material costs from OEM selections\n"
            "- Add applicable testing costs\n"
            "- Compute final commercial totals",
            icon="ℹ️"
        )

# ==================================================
# STEP 2: Review Pricing Results
# ==================================================
if "pricing_result" in st.session_state:
    pricing = st.session_state.pricing_result

    st.divider()
    st.subheader("② Pricing Breakdown")

    # ---------------------------
    # MATERIALS
    # ---------------------------
    st.markdown("### 🏷️ Material Costs")
    if pricing.get("materials"):
        st.dataframe(pricing["materials"], use_container_width=True)
    else:
        st.caption("No material costs computed.")

    # ---------------------------
    # TESTS
    # ---------------------------
    st.markdown("### 🧪 Testing Costs")
    if pricing.get("tests"):
        st.dataframe(pricing["tests"], use_container_width=True)
    else:
        st.caption("No testing costs applicable.")

    # ---------------------------
    # TOTALS
    # ---------------------------
    st.divider()
    st.subheader("💵 Cost Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Material Total",
        pricing.get("total_material_cost", "—")
    )
    col2.metric(
        "Testing Total",
        pricing.get("total_test_cost", "—")
    )
    col3.metric(
        "Grand Total",
        pricing.get("grand_total", "—")
    )

    st.success("Pricing finalized and ready for report generation 📄")
