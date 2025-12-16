import streamlit as st

# ==================================================
# PAGE CONFIG & STYLING
# ==================================================
st.set_page_config(
    page_title="RFP URL Submission",
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
        max-width: 900px;
        margin: 0 auto;
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
    .section-label {
        font-size: 0.875rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    .section-description {
        font-size: 0.875rem;
        color: #64748b;
        margin-bottom: 1rem;
        display: block;
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
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        border: 2px dashed #e2e8f0;
        border-radius: 6px;
        padding: 1.5rem;
        background: #f8fafc;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #cbd5e1;
        background: #f1f5f9;
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
    
    /* Info card styling */
    .info-card {
        background: #f8fafc;
        border-radius: 8px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
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
    
    /* Stats display */
    .stats-row {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .stat-box {
        flex: 1;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 1rem;
        text-align: center;
    }
    
    .stat-number {
        font-size: 1.75rem;
        font-weight: 600;
        color: #2563eb;
        display: block;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================
st.markdown("""
<div class="main-header">
    <h1> RFP URL Submission</h1>
    <p>Queue RFP URLs for automated processing and analysis</p>
</div>
""", unsafe_allow_html=True)

# ==================================================
# URL INPUT SECTION
# ==================================================
st.markdown('<span class="section-label">Manual URL Entry</span>', unsafe_allow_html=True)
st.markdown('<span class="section-description">Provide RFP URLs in the input area</span>', unsafe_allow_html=True)

urls_text = st.text_area(
    label="Manual URL entry",
    label_visibility="collapsed",
    placeholder="https://example.com/rfp/tender-2024-001\nhttps://example.com/rfp/tender-2024-002\nhttps://example.com/rfp/tender-2024-003",
    height=200,
    help="Enter multiple URLs manually. Each URL should be on a new line."
)

st.markdown("<br>", unsafe_allow_html=True)

# ==================================================
# FILE UPLOAD SECTION
# ==================================================
st.markdown('<span class="section-label">Upload URL List</span>', unsafe_allow_html=True)
st.markdown('<span class="section-description">Upload a text file containing URLs (one per line)</span>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    label="Upload URL list",
    label_visibility="collapsed",
    type=["txt"],
    accept_multiple_files=False,
    help="Upload a plain text file (.txt) with UTF-8 encoding"
)

st.markdown("<br>", unsafe_allow_html=True)

# ==================================================
# SUBMIT BUTTON
# ==================================================
col1, col2, col3 = st.columns([2, 1, 1])
with col3:
    submit = st.button("Submit URLs", type="primary", use_container_width=True)

# ==================================================
# PROCESSING LOGIC
# ==================================================
if submit:
    urls = []
    
    # Collect URLs from text area
    if urls_text:
        urls.extend([u.strip() for u in urls_text.splitlines() if u.strip()])
    
    # Collect URLs from uploaded file
    if uploaded_file is not None:
        try:
            file_urls = uploaded_file.read().decode("utf-8").splitlines()
            urls.extend([u.strip() for u in file_urls if u.strip()])
        except Exception as e:
            st.error("❌ Failed to read the uploaded file. Please ensure it's a valid .txt file with UTF-8 encoding.")
            st.stop()
    
    # Validation
    if not urls:
        st.warning("⚠️ No valid URLs were provided. Please enter or upload at least one URL.")
        st.stop()
    
    # Remove duplicates while preserving order
    unique_urls = []
    seen = set()
    for url in urls:
        if url not in seen:
            unique_urls.append(url)
            seen.add(url)
    
    # Store in session state
    st.session_state.urls = unique_urls
    
    # Success message
    st.success(f"✅ **{len(unique_urls)} URL(s)** queued successfully and ready for processing")
    
    # Show duplicate info if any
    if len(urls) > len(unique_urls):
        duplicates_count = len(urls) - len(unique_urls)
        st.info(f"ℹ️ {duplicates_count} duplicate URL(s) were automatically removed")
    
    # Display statistics
    st.markdown("""
    <div class="stats-row">
        <div class="stat-box">
            <span class="stat-number">{}</span>
            <span class="stat-label">Total Submitted</span>
        </div>
        <div class="stat-box">
            <span class="stat-number">{}</span>
            <span class="stat-label">Unique URLs</span>
        </div>
        <div class="stat-box">
            <span class="stat-number">{}</span>
            <span class="stat-label">Duplicates Removed</span>
        </div>
    </div>
    """.format(len(urls), len(unique_urls), len(urls) - len(unique_urls)), unsafe_allow_html=True)
    
    # Show preview of submitted URLs
    with st.expander("📝 View Submitted URLs", expanded=False):
        for idx, url in enumerate(unique_urls, 1):
            st.text(f"{idx}. {url}")

# ==================================================
# EXISTING QUEUE DISPLAY
# ==================================================
if "urls" in st.session_state and st.session_state.urls and not submit:
    st.divider()
    st.markdown("### 📊 Current Queue Status")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"ℹ️ **{len(st.session_state.urls)} URL(s)** currently in queue")
    with col2:
        if st.button("Clear Queue", use_container_width=True):
            st.session_state.urls = []
            st.rerun()
    
    with st.expander("📋 View Queued URLs", expanded=False):
        for idx, url in enumerate(st.session_state.urls, 1):
            st.text(f"{idx}. {url}")