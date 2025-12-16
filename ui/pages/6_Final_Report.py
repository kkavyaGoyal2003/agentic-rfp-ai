import streamlit as st

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Final RFP Report",
    layout="wide",
    initial_sidebar_state="expanded"
)
from sidebar import app_sidebar
app_sidebar()

# ==================================================
# SHARED STYLING (MATCHES MAIN AGENT)
# ==================================================
st.markdown("""
<style>
    .main > div { padding-top: 2rem; }

    .main-header {
        background: #ffffff;
        padding: 2rem 2rem 1.5rem 2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        border-bottom: 3px solid #16a34a;
    }

    .main-header h1 {
        color: #1e293b;
        margin: 0;
        font-size: 2.2rem;
        font-weight: 600;
    }

    .main-header p {
        color: #64748b;
        margin-top: 0.5rem;
        font-size: 1rem;
    }

    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #e5e7eb;
    }

    .section-number {
        background: #16a34a;
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
    }

    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f2937;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.6rem;
        font-weight: 600;
        color: #1e293b;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        font-weight: 500;
        color: #64748b;
    }

    .status-complete {
        background: #dcfce7;
        color: #166534;
        padding: 0.4rem 0.75rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================
st.markdown("""
<div class="main-header">
    <h1>📄 Final RFP Response</h1>
    <p>Consolidated technical, commercial, and compliance-ready submission package</p>
</div>
""", unsafe_allow_html=True)

# ==================================================
# GUARD
# ==================================================
if "final_rfp_response" not in st.session_state:
    st.info("No finalized RFP response available yet.")
    st.stop()

final_report = st.session_state.final_rfp_response
pdf_path = st.session_state.get("final_pdf_path")

# ==================================================
# SECTION 1 — RFP SUMMARY
# ==================================================
st.markdown("""
<div class="section-header">
    <div class="section-number">1</div>
    <div class="section-title">RFP Summary</div>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "RFP Reference",
        final_report.get("rfp_reference", "—")
    )

    col2.metric(
        "Material Cost",
        f"₹ {final_report['totals']['material_cost']:,.0f}"
    )

    col3.metric(
        "Test Cost",
        f"₹ {final_report['totals']['test_cost']:,.0f}"
    )

    col4.markdown(
        "<span class='status-complete'>READY FOR SUBMISSION</span>",
        unsafe_allow_html=True
    )

# ==================================================
# SECTION 2 — COMMERCIAL OFFER
# ==================================================
st.markdown("""
<div class="section-header">
    <div class="section-number">2</div>
    <div class="section-title">Consolidated Commercial Offer</div>
</div>
""", unsafe_allow_html=True)

pricing_table = final_report.get("consolidated_pricing_table", [])

if pricing_table:
    st.dataframe(
        pricing_table,
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("No commercial line items available.")

# ==================================================
# SECTION 3 — TESTING & ACCEPTANCE
# ==================================================
st.markdown("""
<div class="section-header">
    <div class="section-number">3</div>
    <div class="section-title">Testing & Acceptance Charges</div>
</div>
""", unsafe_allow_html=True)

tests = final_report.get("tests", [])

if tests:
    st.dataframe(
        tests,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No testing charges applicable.")

# ==================================================
# SECTION 4 — COST SUMMARY
# ==================================================
st.markdown("""
<div class="section-header">
    <div class="section-number">4</div>
    <div class="section-title">Cost Summary</div>
</div>
""", unsafe_allow_html=True)

totals = final_report.get("totals", {})

c1, c2, c3 = st.columns(3)

c1.metric(
    "Material Cost",
    f"₹ {totals.get('material_cost', 0):,.0f}"
)

c2.metric(
    "Test Cost",
    f"₹ {totals.get('test_cost', 0):,.0f}"
)

c3.metric(
    "Grand Total",
    f"₹ {totals.get('grand_total', 0):,.0f}"
)

# ==================================================
# SECTION 5 — OUTPUT
# ==================================================
st.markdown("""
<div class="section-header">
    <div class="section-number">5</div>
    <div class="section-title">Submission Artifacts</div>
</div>
""", unsafe_allow_html=True)

if pdf_path:
    st.success("📄 Final submission PDF generated successfully")
    st.code(pdf_path)
else:
    st.info("PDF generation pending or handled externally.")

# ==================================================
# AUDIT / DEBUG
# ==================================================
with st.expander("🔍 Full Final JSON Output"):
    st.json(final_report)
