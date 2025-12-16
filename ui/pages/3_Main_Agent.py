import streamlit as st
from agents.main_agent.main_agent import run_main_draft

st.set_page_config(page_title="Main Agent", layout="wide")
st.title("🧠 Main Agent")

# -------------------------------
# GUARD: Sales Agent output
# -------------------------------
if "results" not in st.session_state or not st.session_state.results:
    st.info("No Sales Agent output available yet.")
    st.stop()

rfp = st.session_state.results.get("selected_rfp")
if not rfp:
    st.warning("Sales Agent did not select any eligible RFP.")
    st.stop()

# -------------------------------
# RFP METADATA
# -------------------------------
st.subheader("📄 Selected RFP")
st.json({
    "Tender Reference": rfp.get("tender_reference"),
    "Source URL": rfp.get("source_url"),
    "Submission Due Date": rfp.get("submission_due_date"),
})

# -------------------------------
# STEP 1: Generate Main Draft
# -------------------------------
if "main_draft" not in st.session_state:
    if st.button("🧠 Generate Main Agent Draft"):
        with st.spinner("Preparing technical context..."):
            st.session_state.main_draft = run_main_draft(rfp)

# -------------------------------
# STEP 2: Edit Technical Summary
# -------------------------------
if "main_draft" in st.session_state:
    draft = st.session_state.main_draft

    st.divider()
    st.subheader("✍️ Technical Summary (Editable)")

    technical_summary = st.text_area(
        "🔧 Technical Context for Technical Agent",
        value=draft.get("technical_summary", ""),
        height=280
    )

    if st.button("➡️ Send to Technical Agent"):
        st.session_state.main_approved = {
            **draft,
            "technical_summary": technical_summary
        }
        st.success("Technical context approved and sent to Technical Agent ✅")

# -------------------------------
# STEP 3: Show Technical Results
# -------------------------------
if "main_with_technical" in st.session_state:
    main_result = st.session_state.main_with_technical
    st.divider()
    st.subheader("📦 Technical Agent Results Received")

    for item in main_result.get("technical_recommendations", []):
        with st.expander(f"RFP Item {item['rfp_item_id']} — {item['category']}"):
            oems = item.get("top_oem_recommendations", [])
            if not oems:
                st.warning("No OEM matches found.")
                continue
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

# -------------------------------
# STEP 4: Prepare & Send to Pricing Agent
# -------------------------------
if "main_with_technical" in st.session_state:
    st.divider()
    st.subheader("💰 Prepare Pricing Context")

    # Editable testing/pricing summary
    pricing_summary = st.text_area(
        "Testing / Pricing Summary",
        value=draft.get("pricing_summary", ""),
        height=200
    )

    if st.button("➡️ Send to Pricing Agent"):
        st.session_state.main_to_pricing = {
            **st.session_state.main_with_technical,
            "pricing_summary": pricing_summary
        }
        st.success("Pricing context ready and sent to Pricing Agent ✅")

# -------------------------------
# STEP 5: Show Final Report Ready
# -------------------------------
if "main_with_pricing" in st.session_state:
    st.divider()
    st.success("✅ Final RFP Response Ready! Go to Reports page to view the consolidated report.")
