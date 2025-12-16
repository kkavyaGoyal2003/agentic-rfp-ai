import streamlit as st
from agents.sales_agent import run_sales_agent
from state import init_state
from components.url_card import render_url_card

# ==================================================
# PAGE CONFIG & STYLING
# ==================================================
st.set_page_config(
    page_title="Sales Agent",
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
    
    /* URL Card styling */
    .url-card {
        background: #f8fafc;
        border-radius: 8px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    
    .url-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .url-icon {
        font-size: 1.25rem;
    }
    
    .url-text {
        font-size: 1rem;
        font-weight: 500;
        color: #1f2937;
        word-break: break-all;
    }
    
    /* Progress step styling */
    .progress-step {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.875rem 1rem;
        background: #ffffff;
        border-radius: 6px;
        margin-bottom: 0.5rem;
        border-left: 3px solid #e2e8f0;
        transition: all 0.2s ease;
    }
    
    .progress-step.pending {
        background: #f9fafb;
        border-left-color: #d1d5db;
    }
    
    .progress-step.running {
        background: #eff6ff;
        border-left-color: #2563eb;
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    .progress-step.done {
        background: #ecfdf5;
        border-left-color: #10b981;
    }
    
    .progress-step.skipped {
        background: #fef3c7;
        border-left-color: #f59e0b;
    }
    
    .progress-step.error {
        background: #fef2f2;
        border-left-color: #ef4444;
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: .8;
        }
    }
    
    .step-icon {
        font-size: 1.25rem;
        min-width: 24px;
        text-align: center;
    }
    
    .step-content {
        flex: 1;
    }
    
    .step-title {
        font-size: 0.9375rem;
        font-weight: 600;
        color: #1f2937;
        margin: 0;
    }
    
    .step-status {
        font-size: 0.8125rem;
        color: #64748b;
        margin: 0.25rem 0 0 0;
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
    
    /* Result card styling */
    .result-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.5rem;
    }
    
    .result-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .result-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: #1f2937;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================
st.markdown("""
<div class="main-header">
    <h1>Sales Agent</h1>
    <p>Scan portal URLs to detect RFPs due within three months, extract metadata, and evaluate eligibility.</p>
</div>
""", unsafe_allow_html=True)

init_state()

# ==================================================
# GUARD: No URLs
# ==================================================
if not st.session_state.get("urls"):
    st.info(" **No URLs Submitted**  \nPlease add RFP portal URLs from the Input page to begin analysis.", icon="ℹ️")
    st.stop()

# ==================================================
# URL OVERVIEW
# ==================================================
st.markdown("""
<div class="section-header">
    <div class="section-number">1</div>
    <div class="section-title">RFP Sources</div>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.metric("URLs Configured", len(st.session_state.urls))
        for idx, url in enumerate(st.session_state.urls, 1):
            st.caption(f"{idx}. {url}")
    
    with col2:
        if st.button("🚀 Run Analysis", use_container_width=True, type="primary"):
            st.session_state.running = True
            st.session_state.events = []
            st.session_state.results = None
            st.rerun()

# ==================================================
# PROCESSING STATUS
# ==================================================
if st.session_state.get("running") or st.session_state.get("events"):
    st.markdown("""
    <div class="section-header">
        <div class="section-number">2</div>
        <div class="section-title">Processing Status</div>
    </div>
    """, unsafe_allow_html=True)

status_placeholder = st.empty()

# ==================================================
# RUN PIPELINE (STREAMING)
# ==================================================
if st.session_state.get("running"):
    for event in run_sales_agent(urls=st.session_state.urls):
        st.session_state.events.append(event)
        
        # Live UI update
        with status_placeholder.container():
            for url in st.session_state.urls:
                render_url_card(url, st.session_state.events)
        
        if event["type"] == "FINAL_RESULT":
            st.session_state.results = event["data"]
            st.session_state.running = False
            break

# ==================================================
# DISPLAY EXISTING PROGRESS
# ==================================================
elif st.session_state.get("events"):
    with status_placeholder.container():
        for url in st.session_state.urls:
            render_url_card(url, st.session_state.events)

# ==================================================
# FINAL RESULTS
# ==================================================
if st.session_state.get("results"):
    st.markdown("""
    <div class="section-header">
        <div class="section-number">3</div>
        <div class="section-title">Analysis Results</div>
    </div>
    """, unsafe_allow_html=True)
    
    selected = st.session_state.results.get("selected_rfp")
    
    if not selected:
        st.warning("⚠️ No eligible RFP found in the analyzed sources.", icon="⚠️")
    else:
        st.success(" **Eligible RFP Identified**  \nRFP has been forwarded to Main Agent.", icon="✅")
        
        with st.container(border=True):
            st.markdown("##### 📄 Selected RFP Details")
            st.json(selected, expanded=True)
            
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("➡️ Continue to Main Agent", use_container_width=True, type="primary"):
                    st.switch_page("pages/3_Main_Agent.py")