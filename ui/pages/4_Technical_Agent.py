import streamlit as st
from agents.technical_agent.technical_agent import run_technical_agent

st.set_page_config(page_title="Technical Agent", layout="wide")
st.title("🧪 Technical Agent")
st.caption("Match RFP technical specifications with OEM product catalog")

# ==================================================
# GUARD: Await Main Agent Approval
# ==================================================
if "main_approved" not in st.session_state:
    st.info("Waiting for Main Agent to approve technical context.")
    st.stop()

main_result = st.session_state.main_approved

# ==================================================
# INPUT: Context from Main Agent
# ==================================================
with st.container(border=True):
    st.subheader("📥 Input from Main Agent")

    col1, col2 = st.columns(2)
    col1.metric(
        "RFP Reference",
        main_result["rfp_metadata"].get("tender_reference", "—")
    )
    col2.metric(
        "Scope Items",
        len(main_result.get("product_table", []))
    )

    with st.expander("🔍 View Full Main Agent Context"):
        st.json({
            "RFP Metadata": main_result["rfp_metadata"],
            "Extracted Product Table": main_result.get("product_table", [])
        })

# ==================================================
# STEP 1: Run Technical Agent
# ==================================================
st.divider()
st.subheader("① Run Technical Matching")

if "technical_result" not in st.session_state:
    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("🧪 Run Technical Agent", use_container_width=True):
            with st.spinner("Evaluating spec matches across OEM catalog..."):
                st.session_state.technical_result = run_technical_agent(main_result)

    with col2:
        st.info(
            "The Technical Agent will:\n"
            "- Match each RFP item to OEM SKUs\n"
            "- Score spec alignment (%)\n"
            "- Recommend top 3 products per item",
            icon="ℹ️"
        )

# ==================================================
# STEP 2: Review Technical Results
# ==================================================
if "technical_result" in st.session_state:
    tech = st.session_state.technical_result

    st.divider()
    st.subheader("② Technical Matching Results")

    st.caption("Review top OEM recommendations per RFP line item")

    for item in tech["rfp_items"]:
        title = f"RFP Item {item['rfp_item_id']} — {item['category']}"
        with st.expander(title):
            oems = item["top_oem_recommendations"]

            if not oems:
                st.warning("No OEM matches found for this item.")
                continue

            st.dataframe(
                [
                    {
                        "Rank": idx + 1,
                        "Product Name": oem.get("product_name"),
                        "SKU": oem.get("sku"),
                        "Spec Match (%)": oem.get("score"),
                    }
                    for idx, oem in enumerate(oems)
                ],
                use_container_width=True
            )

# ==================================================
# STEP 3: Send Results Back to Main Agent
# ==================================================
if "technical_result" in st.session_state:
    st.divider()

    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button("➡️ Send to Main Agent", use_container_width=True):
            st.session_state.main_with_technical = {
                **main_result,
                "technical_recommendations": tech["rfp_items"]
            }
            st.success("Technical recommendations sent to Main Agent ✅")

    with col2:
        st.caption(
            "Once approved, these recommendations will be used for pricing estimation."
        )
