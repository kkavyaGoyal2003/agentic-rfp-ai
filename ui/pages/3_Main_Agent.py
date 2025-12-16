import streamlit as st
from agents.main_agent.main_agent import run_main_draft
from agents.main_agent.src.consolidate_response import consolidate_rfp_response

# ==================================================
# PAGE CONFIG & STYLING
# ==================================================
st.set_page_config(
    page_title="Main Agent Orchestrator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main container styling */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Header styling */
    .main-header {
        background: #ffffff;
        padding: 2rem 2rem 1.5rem 2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        border-bottom: 3px solid #2563eb;
    }
    
    .main-header h1 {
        color: #1e293b;
        margin: 0;
        font-size: 2.2rem;
        font-weight: 600;
    }
    
    .main-header p {
        color: #64748b;
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
    }
    
    /* Section styling */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #e0e0e0;
    }
    
    .section-number {
        background: #2563eb;
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 1rem;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f2937;
    }
    
    /* Card styling */
    .info-card {
        background: #f8fafc;
        border-radius: 8px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e293b;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        font-weight: 500;
        color: #64748b;
    }
    
    /* Button styling */
    .stButton > button {
        background: #2563eb;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.625rem 1.5rem;
        font-weight: 500;
        transition: background-color 0.2s ease;
    }
    
    .stButton > button:hover {
        background: #1d4ed8;
    }
    
    /* Text area styling */
    .stTextArea textarea {
        border-radius: 6px;
        border: 1px solid #e2e8f0;
        padding: 0.875rem;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        font-size: 0.875rem;
        line-height: 1.6;
    }
    
    .stTextArea textarea:focus {
        border-color: #2563eb;
        outline: none;
    }
    
    /* Progress indicator */
    .progress-step {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        background: #f9fafb;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    
    .progress-step.completed {
        background: #ecfdf5;
        border-left: 4px solid #10b981;
    }
    
    .progress-step.active {
        background: #eff6ff;
        border-left: 4px solid #2563eb;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: #f9fafb;
        border-radius: 8px;
        font-weight: 600;
        color: #374151;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .status-pending {
        background: #fef3c7;
        color: #92400e;
    }
    
    .status-complete {
        background: #d1fae5;
        color: #065f46;
    }
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================
st.markdown("""
<div class="main-header">
    <h1>🧠 Main Agent Orchestrator</h1>
    <p>Intelligent coordination of RFP analysis, technical matching, and pricing synthesis</p>
</div>
""", unsafe_allow_html=True)

# ==================================================
# GUARD: Sales Agent output
# ==================================================
if "results" not in st.session_state or not st.session_state.results:
    st.info("🔒 **Prerequisites Required**  \nPlease complete the Sales Agent workflow to proceed with RFP orchestration.", icon="ℹ️")
    st.stop()

rfp = st.session_state.results.get("selected_rfp")
if not rfp:
    st.warning("⚠️ No eligible RFP was selected by the Sales Agent.", icon="⚠️")
    st.stop()

# ==================================================
# SELECTED RFP OVERVIEW
# ==================================================
st.markdown("""
<div class="section-header">
    <div class="section-number">1</div>
    <div class="section-title">Selected RFP Overview</div>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric(
        "Tender Reference",
        rfp.get("tender_reference", "—")
    )
    col2.metric(
        "Due Date",
        rfp.get("submission_due_date", "—")
    )
    col3.metric(
        "Source",
        "LSTK Portal"
    )
    col4.metric(
        "Status",
        "Active"
    )
    
    with st.expander("📋 View Complete RFP Metadata", expanded=False):
        st.json(rfp, expanded=True)

# ==================================================
# CONTEXT GENERATION
# ==================================================
st.markdown("""
<div class="section-header">
    <div class="section-number">2</div>
    <div class="section-title">Context Generation</div>
</div>
""", unsafe_allow_html=True)

if "main_draft" not in st.session_state:
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4 style="margin-top:0;">🎯 What This Does</h4>
            <p style="margin-bottom:0;">Analyzes the RFP and generates role-specific context for:</p>
            <ul style="margin-bottom:0;">
                <li><strong>Technical Agent:</strong> Product specs and scope</li>
                <li><strong>Pricing Agent:</strong> Testing and acceptance criteria</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🚀 Generate Context", use_container_width=True, type="primary"):
            with st.spinner("🔄 Analyzing RFP structure and extracting key requirements..."):
                st.session_state.main_draft = run_main_draft(rfp)
                st.rerun()
else:
    st.success("✅ Context generation completed", icon="✅")

# ==================================================
# TECHNICAL SUMMARY REVIEW
# ==================================================
if "main_draft" in st.session_state:
    draft = st.session_state.main_draft
    
    st.markdown("""
    <div class="section-header">
        <div class="section-number">3</div>
        <div class="section-title">Technical Context Review</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("##### 📝 Technical Summary for SKU Matching")
        st.caption("This context will be shared with the Technical Agent for product matching. Review and refine as needed.")
        
        technical_summary = st.text_area(
            "Technical Summary",
            value=draft.get("technical_summary", ""),
            height=300,
            label_visibility="collapsed"
        )
        
        col1, col2, col3 = st.columns([2, 2, 3])
        
        with col1:
            if st.button("✏️ Reset to Original", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("➡️ Send to Technical Agent", use_container_width=True, type="primary"):
                st.session_state.main_approved = {
                    **draft,
                    "technical_summary": technical_summary
                }
                st.success("✅ Technical context approved and routed", icon="✅")
                st.balloons()

# ==================================================
# TECHNICAL RESULTS
# ==================================================
if "main_with_technical" in st.session_state:
    main_result = st.session_state.main_with_technical
    
    st.markdown("""
    <div class="section-header">
        <div class="section-number">4</div>
        <div class="section-title">Technical Agent Results</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("📊 **OEM Product Recommendations**  \nTop 3 matching products per RFP line item, ranked by specification match score", icon="📊")
    
    recommendations = main_result.get("technical_recommendations", [])
    
    if recommendations:
        cols = st.columns(min(len(recommendations), 3))
        
        for idx, item in enumerate(recommendations):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"**Item {item['rfp_item_id']}**")
                    st.caption(item['category'])
                    
                    oems = item.get("top_oem_recommendations", [])
                    if oems and len(oems) > 0:
                        top_match = oems[0].get("score", 0)
                        st.metric("Best Match", f"{top_match}%")
        
        st.divider()
        
        for item in recommendations:
            title = f"🔧 RFP Item {item['rfp_item_id']} — {item['category']}"
            with st.expander(title, expanded=False):
                oems = item.get("top_oem_recommendations", [])
                
                if not oems:
                    st.warning("No OEM matches found for this item")
                    continue
                
                st.dataframe(
                    [
                        {
                            "Rank": f"#{idx + 1}",
                            "Product Name": oem.get("product_name", "—"),
                            "SKU": oem.get("sku", "—"),
                            "Match Score": f"{oem.get('score', 0)}%",
                        }
                        for idx, oem in enumerate(oems)
                    ],
                    use_container_width=True,
                    hide_index=True
                )
    else:
        st.warning("No technical recommendations available")

# ==================================================
# PRICING CONTEXT REVIEW
# ==================================================
if "main_with_technical" in st.session_state:
    st.markdown("""
    <div class="section-header">
        <div class="section-number">5</div>
        <div class="section-title">Pricing Context Review</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("##### 💰 Testing & Acceptance Summary")
        st.caption("This context will be shared with the Pricing Agent for cost estimation. Ensure test requirements are clear.")
        
        pricing_summary = st.text_area(
            "Pricing Summary",
            value=draft.get("pricing_summary", ""),
            height=220,
            label_visibility="collapsed"
        )
        
        col1, col2, col3 = st.columns([2, 2, 3])
        
        with col1:
            if st.button("✏️ Reset to Original ", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("➡️ Send to Pricing Agent", use_container_width=True, type="primary"):
                st.session_state.main_to_pricing = {
                    **st.session_state.main_with_technical,
                    "pricing_summary": pricing_summary
                }
                st.success("✅ Pricing context approved and routed", icon="✅")
                st.balloons()

# ==================================================
# COMPLETION STATE
# ==================================================
if "main_with_pricing" in st.session_state:
    st.markdown("""
    <div class="section-header">
        <div class="section-number">6</div>
        <div class="section-title">Workflow Complete</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.success("""
    #### ✅ RFP Response Package Ready
    
    All agent workflows have been completed successfully. The consolidated RFP response includes:
    - ✓ Technical product recommendations with match scores
    - ✓ Detailed pricing breakdown with test costs
    - ✓ Complete compliance documentation
    
    **Next Step:** Navigate to the **📊 Reports** page to review and export the final submission package.
    """, icon="🎉")
    
    # --------------------------------------------------
    # CONSOLIDATE FINAL RESPONSE
    # --------------------------------------------------
    final_rfp_response = consolidate_rfp_response(
        main_result=st.session_state.main_draft,
        technical_result=st.session_state.technical_result,
        pricing_result=st.session_state.pricing_result
    )
    

    # --------------------------------------------------
    # STORE FOR REPORTS PAGE
    # --------------------------------------------------
    st.session_state.final_rfp_response = final_rfp_response
    
    if st.button("📊 View Final Report", use_container_width=True, type="primary"):
        st.switch_page("pages/6_Final_Report.py")