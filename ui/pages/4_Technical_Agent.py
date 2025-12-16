import streamlit as st
from agents.technical_agent.technical_agent import run_technical_agent

st.set_page_config(page_title="Technical Agent", layout="wide")
st.title("🧪 Technical Agent")

# -------------------------------------------------
# GUARD: Must receive approved Main Agent output
# -------------------------------------------------
if "main_approved" not in st.session_state:
    st.info("Waiting for Main Agent approval.")
    st.stop()

main_result = st.session_state.main_approved

st.subheader("📦 Input from Main Agent")
with st.expander("View Main Agent Data"):
    st.json({
        "RFP Reference": main_result["rfp_metadata"].get("tender_reference"),
        "Product Table Items": len(main_result.get("product_table", []))
    })

# -------------------------------------------------
# RUN TECHNICAL AGENT
# -------------------------------------------------
if "technical_result" not in st.session_state:
    if st.button("🧪 Run Technical Agent"):
        with st.spinner("Matching RFP specs with OEM products..."):
            st.session_state.technical_result = run_technical_agent(main_result)

# -------------------------------------------------
# DISPLAY RESULTS
# -------------------------------------------------
if "technical_result" in st.session_state:
    tech = st.session_state.technical_result

    st.divider()
    st.subheader("✅ Technical Matching Results")

    for item in tech["rfp_items"]:
        with st.expander(f"RFP Item {item['rfp_item_id']} — {item['category']}"):
            oems = item["top_oem_recommendations"]

            if not oems:
                st.warning("No OEM matches found.")
                continue

            # Show top OEMs as table
            st.dataframe(
                [
                    {
                        "Rank": idx + 1,
                        "Product Name": oem.get("product_name"),
                        "SKU": oem.get("sku"),
                        "Spec Match %": oem.get("score"),
                    }
                    for idx, oem in enumerate(oems)
                ],
                use_container_width=True
            )

    # -------------------------------------------------
    # SEND BACK TO MAIN AGENT
    # -------------------------------------------------
    if st.button("➡️ Send Technical Results to Main Agent"):
        st.session_state.main_with_technical = {
            **main_result,
            "technical_recommendations": tech["rfp_items"]
        }

        st.success("Technical results sent back to Main Agent ✅")
