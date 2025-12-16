import streamlit as st
from agents.technical_agent.technical_agent import run_technical_agent

# ==================================================
# PAGE CONFIG & STYLING
# ==================================================
st.set_page_config(
    page_title="Technical Agent",
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
    
    /* Progress badge */
    .status-badge {
        display: inline-block;
        padding: 0.375rem 0.875rem;
        border-radius: 6px;
        font-size: 0.875rem;
        font-weight: 500;
        background: #dbeafe;
        color: #1e40af;
    }
    
    /* Match score styling */
    .match-high {
        color: #059669;
        font-weight: 600;
    }
    
    .match-medium {
        color: #d97706;
        font-weight: 600;
    }
    
    .match-low {
        color: #dc2626;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================
st.markdown("""
<div class="main-header">
    <h1>Technical Agent</h1>
    <p>Intelligent product matching and specification alignment analysis</p>
</div>
""", unsafe_allow_html=True)

# ==================================================
# GUARD: Await Main Agent Approval
# ==================================================
if "main_approved" not in st.session_state:
    st.info("🔒 **Awaiting Input**  \nThe Technical Agent requires approved context from the Main Agent to proceed.", icon="ℹ️")
    st.stop()

main_result = st.session_state.main_approved

# ==================================================
# INPUT FROM MAIN AGENT
# ==================================================
st.markdown("""
<div class="section-header">
    <div class="section-number">1</div>
    <div class="section-title">Input Context</div>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    
    col1.metric(
        "RFP Reference",
        main_result["rfp_metadata"].get("tender_reference", "—")
    )
    col2.metric(
        "Line Items",
        len(main_result.get("product_table", [])) - 1
    )
    col3.metric(
        "Status",
        "Ready for Analysis"
    )
    
    with st.expander("📋 View Technical Context from Main Agent", expanded=False):
        st.markdown("##### Technical Summary")
        st.text_area(
            "Technical Context",
            value=main_result.get("technical_summary", "No summary available"),
            height=200,
            disabled=True,
            label_visibility="collapsed"
        )
        
        st.markdown("##### Product Table")
        if main_result.get("product_table"):
            st.dataframe(
                main_result["product_table"],
                use_container_width=True,
                hide_index=True
            )

# ==================================================
# RUN TECHNICAL MATCHING
# ==================================================
st.markdown("""
<div class="section-header">
    <div class="section-number">2</div>
    <div class="section-title">Technical Matching</div>
</div>
""", unsafe_allow_html=True)

if "technical_result" not in st.session_state:
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>🔍 Analysis Process</h4>
            <ul>
                <li>Parse RFP specifications</li>
                <li>Query OEM product catalog</li>
                <li>Calculate spec match scores</li>
                <li>Rank top 3 products per item</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Run Technical Analysis", use_container_width=True, type="primary"):
            with st.spinner("🔄 Analyzing specifications and matching against OEM catalog..."):
                st.session_state.technical_result = run_technical_agent(main_result)
                st.rerun()
else:
    st.success("Technical matching completed successfully", icon="✅")

# ==================================================
# TECHNICAL RESULTS
# ==================================================
if "technical_result" in st.session_state:
    tech = st.session_state.technical_result
    
    st.markdown("""
    <div class="section-header">
        <div class="section-number">3</div>
        <div class="section-title">Matching Results</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("📊 **OEM Product Recommendations**  \nTop 3 matching products for each RFP line item, ranked by specification alignment", icon="📊")
    
    # Summary metrics
    rfp_items = tech.get("rfp_items", [])
    total_items = len(rfp_items)
    matched_items = sum(1 for item in rfp_items if item.get("top_oem_recommendations"))
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Items", total_items)
    col2.metric("Successfully Matched", matched_items)
    col3.metric("Match Rate", f"{(matched_items/total_items*100):.0f}%" if total_items > 0 else "0%")
    
    st.divider()
    
    # Detailed results per item
    for item in rfp_items:
        item_id = item.get('rfp_item_id', 'Unknown')
        category = item.get('category', 'Unknown Category')
        title = f"🔧 Item {item_id} — {category}"
        
        with st.expander(title, expanded=False):
            oems = item.get("top_oem_recommendations", [])
            
            if not oems:
                st.warning("⚠️ No suitable OEM matches found for this specification")
                continue
            
            # Display top match prominently
            top_match = oems[0]
            col1, col2 = st.columns([2, 3])
            
            with col1:
                st.markdown("##### 🏆 Best Match")
                st.markdown(f"**{top_match.get('product_name', 'Unknown')}**")
                st.caption(f"SKU: {top_match.get('sku', '—')}")
                
                score = top_match.get('score', 0)
                score_class = "match-high" if score >= 80 else "match-medium" if score >= 60 else "match-low"
                st.markdown(f"<p class='{score_class}'>Match Score: {score}%</p>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("##### 📊 All Recommendations")
                st.dataframe(
                    [
                        {
                            "Rank": f"#{idx + 1}",
                            "Product": oem.get("product_name", "—"),
                            "SKU": oem.get("sku", "—"),
                            "Match Score": f"{oem.get('score', 0)}%",
                        }
                        for idx, oem in enumerate(oems)
                    ],
                    use_container_width=True,
                    hide_index=True
                )

# ==================================================
# SEND TO MAIN AGENT
# ==================================================
if "technical_result" in st.session_state:
    st.markdown("""
    <div class="section-header">
        <div class="section-number">4</div>
        <div class="section-title">Route Results</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.markdown("##### ✅ Analysis Complete")
            st.markdown("""
            Technical matching has been completed successfully. The recommendations are ready to be sent to the Main Agent for consolidation with pricing data.
            """)
        
        with col2:
            st.markdown("##### 📤 Next Steps")
            if st.button("➡️ Send to Main Agent", use_container_width=True, type="primary"):
                st.session_state.main_with_technical = {
                    **main_result,
                    "technical_recommendations": tech["rfp_items"]
                }
                st.success("✅ Technical recommendations successfully routed to Main Agent", icon="✅")
                st.balloons()
            else:
                st.caption("Results will be used for pricing estimation and final RFP response preparation")