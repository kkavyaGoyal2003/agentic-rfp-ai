import streamlit as st
from agents.main_agent.main_agent import run_main_draft

st.set_page_config(page_title="Main Agent", layout="wide")
st.title("🧠 Main Agent Orchestrator")
st.caption("Review, refine, and route RFP context across agents")

# ==================================================
# GUARD: Sales Agent output
# ==================================================
if "results" not in st.session_state or not st.session_state.results:
    st.info("No Sales Agent output available yet. Please complete Sales Agent step.")
    st.stop()

rfp = st.session_state.results.get("selected_rfp")
if not rfp:
    st.warning("Sales Agent did not select any eligible RFP.")
    st.stop()

# ==================================================
# SECTION: Selected RFP Overview
# ==================================================
with st.container(border=True):
    st.subheader("📄 Selected RFP")

    col1, col2, col3 = st.columns(3)

    col1.metric("Tender Reference", rfp.get("tender_reference", "—"))
    col2.metric("Submission Due Date", rfp.get("submission_due_date", "—"))
    col3.metric("Source", "LSTK Portal")

    with st.expander("🔍 View Full RFP Metadata"):
        st.json(rfp)

# ==================================================
# STEP 1: Generate Main Agent Draft
# ==================================================
st.divider()
st.subheader("① Generate Main Agent Context")

if "main_draft" not in st.session_state:
    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("🧠 Generate Draft", use_container_width=True):
            with st.spinner("Analyzing RFP and preparing role-specific context..."):
                st.session_state.main_draft = run_main_draft(rfp)

    with col2:
        st.info(
            "This step prepares:\n"
            "- Technical context for SKU matching\n"
            "- Testing & acceptance context for pricing",
            icon="ℹ️"
        )

# ==================================================
# STEP 2: Review & Edit Technical Summary
# ==================================================
if "main_draft" in st.session_state:
    draft = st.session_state.main_draft

    st.divider()
    st.subheader("② Technical Context (Editable)")

    with st.container(border=True):
        technical_summary = st.text_area(
            "Technical Summary shared with Technical Agent",
            value=draft.get("technical_summary", ""),
            height=300
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("➡️ Send to Technical Agent", use_container_width=True):
                st.session_state.main_approved = {
                    **draft,
                    "technical_summary": technical_summary
                }
                st.success("Technical context approved and sent ✅")

        with col2:
            st.caption(
                "You may refine specs, clarify scope, or remove ambiguity before routing."
            )

# ==================================================
# STEP 3: Technical Agent Results
# ==================================================
if "main_with_technical" in st.session_state:
    main_result = st.session_state.main_with_technical

    st.divider()
    st.subheader("③ Technical Agent Output")

    st.caption("Top OEM recommendations per RFP line item")

    for item in main_result.get("technical_recommendations", []):
        title = f"RFP Item {item['rfp_item_id']} — {item['category']}"
        with st.expander(title):
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
                        "Spec Match (%)": oem.get("score"),
                    }
                    for idx, oem in enumerate(oems)
                ],
                use_container_width=True
            )

# ==================================================
# STEP 4: Prepare Pricing Context
# ==================================================
if "main_with_technical" in st.session_state:
    st.divider()
    st.subheader("④ Pricing Context (Editable)")

    with st.container(border=True):
        pricing_summary = st.text_area(
            "Testing & Acceptance Summary for Pricing Agent",
            value=draft.get("pricing_summary", ""),
            height=220
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("➡️ Send to Pricing Agent", use_container_width=True):
                st.session_state.main_to_pricing = {
                    **st.session_state.main_with_technical,
                    "pricing_summary": pricing_summary
                }
                st.success("Pricing context approved and sent ✅")

        with col2:
            st.caption(
                "Focus on testing types, inspection requirements, and site conditions."
            )

# ==================================================
# STEP 5: Final State
# ==================================================
if "main_with_pricing" in st.session_state:
    st.divider()
    st.success(
        "✅ Final RFP response is ready.\n\n"
        "Proceed to **Reports** to view and export the consolidated submission."
    )
