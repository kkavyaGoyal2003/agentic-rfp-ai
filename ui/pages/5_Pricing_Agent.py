import streamlit as st
from agents.pricing_agent.pricing_agent import run_pricing_agent

# ==================================================
# PAGE CONFIG & STYLING
# ==================================================
st.set_page_config(
    page_title="Pricing Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)
from sidebar import app_sidebar
app_sidebar()
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
    
    /* Subsection styling */
    .subsection-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 1.5rem 0 1rem 0;
        font-size: 1.125rem;
        font-weight: 600;
        color: #1e293b;
    }
    
    /* Info card styling */
    .info-card {
        background: #f8fafc;
        border-radius: 8px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    
    .info-card h4 {
        color: #1e293b;
        margin: 0 0 0.75rem 0;
        font-size: 1rem;
        font-weight: 600;
    }
    
    .info-card ul {
        margin: 0;
        padding-left: 1.25rem;
        color: #475569;
    }
    
    .info-card li {
        margin-bottom: 0.375rem;
        font-size: 0.875rem;
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
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: #f9fafb;
        border-radius: 6px;
        font-weight: 500;
        color: #374151;
        border: 1px solid #e5e7eb;
    }
    
    /* Table styling */
    [data-testid="stDataFrame"] {
        border: 1px solid #e2e8f0;
        border-radius: 6px;
    }
    
    /* Cost summary card */
    .cost-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .cost-card .label {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .cost-card .amount {
        font-size: 1.875rem;
        color: #1e293b;
        font-weight: 600;
    }
    
    .cost-card.grand-total {
        background: #eff6ff;
        border: 2px solid #2563eb;
    }
    
    .cost-card.grand-total .amount {
        color: #2563eb;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 2rem;
        color: #64748b;
        font-size: 0.875rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================
st.markdown("""
<div class="main-header">
    <h1>💰 Pricing Agent</h1>
    <p>Comprehensive cost analysis for materials, testing, and project delivery</p>
</div>
""", unsafe_allow_html=True)

# ==================================================
# GUARD: Await Main Agent Pricing Context
# ==================================================
if "main_to_pricing" not in st.session_state:
    st.info("🔒 **Awaiting Input**  \nThe Pricing Agent requires approved context from the Main Agent to proceed.", icon="ℹ️")
    st.stop()

main_result = st.session_state.main_to_pricing


# ==================================================
# INPUT CONTEXT
# ==================================================
st.markdown("""
<div class="section-header">
    <div class="section-number">1</div>
    <div class="section-title">Input Context</div>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric(
        "RFP Reference",
        main_result["rfp_metadata"].get("tender_reference", "—")
    )
    col2.metric(
        "Product Items",
        len(main_result.get("product_table", [])) - 1
    )
    col3.metric(
        "Technical Matches",
        len(main_result.get("technical_recommendations", []))
    )
    col4.metric(
        "Status",
        "Ready for Pricing"
    )
    
    with st.expander("📋 View Complete Pricing Context", expanded=False):
        tab1, tab2, tab3 = st.tabs(["RFP Metadata", "Product Table", "Technical Recommendations"])
        
        with tab1:
            st.json(main_result["rfp_metadata"])
        
        with tab2:
            if main_result.get("product_table"):
                st.dataframe(main_result["product_table"], use_container_width=True, hide_index=True)
            else:
                st.caption("No product table available")
        
        with tab3:
            st.json(main_result.get("technical_recommendations", []))

# ==================================================
# COMPUTE PRICING
# ==================================================
st.markdown("""
<div class="section-header">
    <div class="section-number">2</div>
    <div class="section-title">Cost Computation</div>
</div>
""", unsafe_allow_html=True)

if "pricing_result" not in st.session_state:
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>💵 Pricing Components</h4>
            <ul>
                <li>Material costs per selected SKU</li>
                <li>Testing and acceptance costs</li>
                <li>Site inspection fees</li>
                <li>Compliance documentation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Calculate Pricing", use_container_width=True, type="primary"):
            with st.spinner("🔄 Computing material and testing costs..."):
                pricing = run_pricing_agent(main_result)
                st.session_state.pricing_result = pricing
                
                # Send back to Main Agent
                st.session_state.main_with_pricing = {
                    **main_result,
                    "pricing": pricing
                }
                
                st.rerun()
else:
    st.success("✅ Pricing computation completed successfully", icon="✅")

# ==================================================
# PRICING BREAKDOWN
# ==================================================
if "pricing_result" in st.session_state:
    pricing = st.session_state.pricing_result
    
    st.markdown("""
    <div class="section-header">
        <div class="section-number">3</div>
        <div class="section-title">Pricing Breakdown</div>
    </div>
    """, unsafe_allow_html=True)
    
    # MATERIAL COSTS
    st.markdown('<div class="subsection-header">🏷️ Material Costs</div>', unsafe_allow_html=True)
    
    with st.container(border=True):
        if pricing.get("materials"):
            st.dataframe(
                pricing["materials"],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.markdown('<div class="empty-state">No material costs computed</div>', unsafe_allow_html=True)
    
    # TESTING COSTS
    st.markdown('<div class="subsection-header">🧪 Testing & Acceptance Costs</div>', unsafe_allow_html=True)
    
    with st.container(border=True):
        if pricing.get("tests"):
            st.dataframe(
                pricing["tests"],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.markdown('<div class="empty-state">No testing costs applicable</div>', unsafe_allow_html=True)
    
    # COST SUMMARY
    st.markdown("""
    <div class="section-header">
        <div class="section-number">4</div>
        <div class="section-title">Cost Summary</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="cost-card">
            <div class="label">Material Total</div>
            <div class="amount">{}</div>
        </div>
        """.format(pricing.get("total_material_cost", "₹0")), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="cost-card">
            <div class="label">Testing Total</div>
            <div class="amount">{}</div>
        </div>
        """.format(pricing.get("total_test_cost", "₹0")), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="cost-card grand-total">
            <div class="label">Grand Total</div>
            <div class="amount">{}</div>
        </div>
        """.format(pricing.get("grand_total", "₹0")), unsafe_allow_html=True)
    
    # COMPLETION MESSAGE
    st.markdown("""
    <div class="section-header">
        <div class="section-number">5</div>
        <div class="section-title">Finalize & Route</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.markdown("##### ✅ Pricing Complete")
            st.markdown("""
            All cost calculations have been finalized. The pricing breakdown is ready to be consolidated with technical recommendations for final RFP response.
            """)
        
        with col2:
            st.markdown("##### 📤 Next Steps")
            st.info("📄 Pricing data has been automatically sent to the Main Agent for report generation", icon="✅")
            st.caption("Navigate to the Reports page to view and export the complete RFP response package")