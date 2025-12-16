import streamlit as st
import sys
from pathlib import Path
import graphviz

# ==================================================
# PAGE CONFIG & PROFESSIONAL STYLING
# ==================================================
st.set_page_config(
    page_title="Agentic RFP AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

from sidebar import app_sidebar
app_sidebar()

st.markdown("""
<style>
    .main > div { padding-top: 2rem; }

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

    .info-card {
        background: #f8fafc;
        border-radius: 8px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }

    .stButton > button {
        background: #2563eb;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.625rem 1.5rem;
        font-weight: 500;
    }

    .stButton > button:hover {
        background: #1d4ed8;
    }

    .stTextArea textarea {
        border-radius: 6px;
        border: 1px solid #e2e8f0;
        padding: 0.875rem;
        font-size: 0.875rem;
    }

    .stTextArea textarea:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 1px #2563eb;
    }

    .status-badge {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
    }

    .status-complete {
        background: #d1fae5;
        color: #065f46;
    }

    .status-active {
        background: #dbeafe;
        color: #1e40af;
    }

    .progress-step {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        background: #f9fafb;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #e2e8f0;
    }

    .progress-step.active {
        background: #eff6ff;
        border-left: 4px solid #2563eb;
    }

    .progress-step.completed {
        background: #ecfdf5;
        border-left: 4px solid #10b981;
    }
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================
st.markdown("""
<div class="main-header">
    <h1>🤖 Agentic RFP Response Automation</h1>
    <p>End-to-end multi-agent system for discovering, analyzing, matching, pricing, and consolidating B2B RFPs</p>
</div>
""", unsafe_allow_html=True)

# ==================================================
# PROJECT ROOT SETUP
# ==================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from agents.sales_agent import run_sales_agent
from agents.main_agent.main_agent import run_main_draft
from agents.technical_agent import run_technical_agent
from agents.pricing_agent import run_pricing_agent
from agents.main_agent.src.consolidate_response import consolidate_rfp_response
from agents.main_agent.src.generate_pdf import generate_rfp_response_pdf
from state import init_state

init_state()

# ==================================================
# INPUT LAYER
# ==================================================
st.markdown("""
<div class="section-header">
    <div class="section-number">1</div>
    <div class="section-title">Input Layer: RFP Source URLs</div>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    urls_input = st.text_area(
        "Enter URLs (comma or newline separated)",
        height=120,
        placeholder="https://powergrid-rfp-demo.netlify.app/",
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        start_button = st.button("Start Pipeline", type="primary", use_container_width=True)

if start_button:
    urls = [url.strip() for url in urls_input.replace(',', '\n').split('\n') if url.strip()]
    if urls:
        st.session_state['urls'] = urls
        st.session_state['stage'] = 'sales'
        # Clear previous results
        for key in ['rfp', 'main_result', 'technical_result', 'pricing_result', 'final_rfp_response', 'final_pdf_path']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# ==================================================
# PIPELINE VISUALIZATION
# ==================================================
def render_graph(current_stage):
    dot = graphviz.Digraph(format='svg')
    dot.attr(rankdir='LR', bgcolor='transparent', splines='true')
    dot.attr('node', shape='box', style='filled', fontname='Helvetica', fontsize='12')

    stage_colors = {
        'input': '#bfdbfe',
        'sales': '#fde68a',
        'main_draft': '#fde68a',
        'technical': '#fde68a',
        'pricing': '#fde68a',
        'main_final': '#fde68a',
        'output': '#bbf7d0'
    }

    active_color = '#2563eb'
    completed_color = '#10b981'

    current_fill = stage_colors.get(current_stage, '#f1f5f9')

    dot.node('input', 'Input URLs', fillcolor='#bfdbfe' if current_stage == 'input' else '#f1f5f9')
    dot.node('sales', 'Sales Agent\n', fillcolor=current_fill if current_stage == 'sales' else '#f1f5f9')
    dot.node('main', 'Main Agent\n(Orchestrator)', fillcolor=current_fill if current_stage in ['main_draft', 'main_final'] else '#f1f5f9', shape='diamond')
    dot.node('technical', 'Technical Agent\n', fillcolor=current_fill if current_stage == 'technical' else '#f1f5f9')
    dot.node('pricing', 'Pricing Agent\n', fillcolor=current_fill if current_stage == 'pricing' else '#f1f5f9')
    dot.node('output', 'Final Report\n& PDF', fillcolor=current_fill if current_stage == 'output' else '#f1f5f9')

    dot.edge('input', 'sales')
    dot.edge('sales', 'main')
    dot.edge('main', 'technical')
    dot.edge('main', 'pricing')
    dot.edge('technical', 'main')
    dot.edge('pricing', 'main')
    dot.edge('main', 'output')

    st.graphviz_chart(dot, use_container_width=True)

# ==================================================
# EXECUTION FLOW
# ==================================================
if 'stage' in st.session_state:
    current_stage = st.session_state['stage']
    render_graph(current_stage)

    if current_stage == 'sales':
        st.markdown("""
        <div class="section-header">
            <div class="section-number">2</div>
            <div class="section-title">Sales Agent - RFP Discovery</div>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            placeholder = st.empty()
            rfp = None
            for event in run_sales_agent(urls=st.session_state['urls']):
                if event.get("type") == "STATUS_UPDATE":
                    placeholder.info(f"🔄 {event['data']}")
                if event.get("type") == "FINAL_RESULT":
                    rfp = event["data"]["selected_rfp"]
                    placeholder.success("✅ RFP discovered and selected")
            if rfp:
                st.session_state['rfp'] = rfp
                st.session_state['stage'] = 'main_draft'
                st.rerun()

    elif current_stage == 'main_draft':
        st.markdown("""
        <div class="section-header">
            <div class="section-number">3</div>
            <div class="section-title">Main Agent - Context Generation</div>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("Analyzing RFP and generating role-specific summaries..."):
            main_result = run_main_draft(st.session_state['rfp'])
        st.session_state['main_result'] = main_result
        st.session_state['stage'] = 'technical'
        st.rerun()

    elif current_stage == 'technical':
        st.markdown("""
        <div class="section-header">
            <div class="section-number">4</div>
            <div class="section-title">Technical Agent - Product Matching</div>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("Matching RFP specifications to OEM product catalog..."):
            technical_result = run_technical_agent(st.session_state['main_result'])
        st.session_state['technical_result'] = technical_result
        st.session_state['stage'] = 'pricing'
        st.rerun()

    elif current_stage == 'pricing':
        st.markdown("""
        <div class="section-header">
            <div class="section-number">5</div>
            <div class="section-title">Pricing Agent - Cost Calculation</div>
        </div>
        """, unsafe_allow_html=True)

        pricing_input = {
            **st.session_state['main_result'],
            "technical_recommendations": st.session_state['technical_result']["rfp_items"]
        }
        with st.spinner("Calculating material and testing costs..."):
            pricing_result = run_pricing_agent(pricing_input)
        st.session_state['pricing_result'] = pricing_result
        st.session_state['stage'] = 'main_final'
        st.rerun()

    elif current_stage == 'main_final':
        st.markdown("""
        <div class="section-header">
            <div class="section-number">6</div>
            <div class="section-title">Main Agent - Final Consolidation</div>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("Consolidating technical, pricing, and compliance data..."):
            final_rfp_response = consolidate_rfp_response(
                main_result=st.session_state['main_result'],
                technical_result=st.session_state['technical_result'],
                pricing_result=st.session_state['pricing_result']
            )
            pdf_path = f"data/outputs/RFP_RESPONSE_{st.session_state['main_result']['rfp_metadata']['tender_reference']}.pdf"
            generate_rfp_response_pdf(final_rfp_response, pdf_path)

        st.session_state['final_rfp_response'] = final_rfp_response
        st.session_state['final_pdf_path'] = pdf_path
        st.session_state['stage'] = 'output'
        st.rerun()

    elif current_stage == 'output':
        st.markdown("""
        <div class="section-header">
            <div class="section-number">7</div>
            <div class="section-title">Pipeline Complete - Final RFP Response</div>
        </div>
        """, unsafe_allow_html=True)

        st.success("✅ Full agentic pipeline executed successfully")

        with st.container(border=True):
            st.markdown("<span class='status-badge status-complete'>READY FOR SUBMISSION</span>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("RFP Reference", st.session_state['final_rfp_response'].get("rfp_reference", "—"))
            with col2:
                st.metric("Grand Total", f"₹ {st.session_state['final_rfp_response']['totals'].get('grand_total', 0):,.0f}")

            st.markdown(f"**PDF Generated:** `{st.session_state['final_pdf_path']}`")

        # Optional: Show key sections from final report
        with st.expander("📄 View Consolidated Pricing Table"):
            table = st.session_state['final_rfp_response'].get("consolidated_pricing_table", [])
            if table:
                st.dataframe(table, use_container_width=True, hide_index=True)
            else:
                st.info("No pricing items")

        with st.expander("🔍 Full Final Response JSON"):
            st.json(st.session_state['final_rfp_response'])