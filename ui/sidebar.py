import streamlit as st

def app_sidebar():
    st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none; }

    .nav-btn button {
        padding: 0.65rem 0.75rem;
        margin: 0.15rem 0.5rem;
        border-radius: 8px;
        cursor: pointer;
        font-size: 0.85rem;
        font-weight: 500;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        color: #475569;
        background: none;
        border: none;
        width: 100%;
        text-align: left;
    }

    .nav-btn button:hover {
        background-color: #f1f5f9;
        color: #0f172a;
    }

    .nav-btn.active button {
        background-color: #eff6ff;
        color: #1d4ed8;
        font-weight: 600;
        border-left: 3px solid #1d4ed8;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("""
        <div style="padding:1.25rem 0.75rem 0.75rem;border-bottom:1px solid #e5e7eb;">
            <div style="font-size:1.05rem;font-weight:600;">Agentic RFP AI</div>
            <div style="font-size:0.8rem;color:#64748b;">Multi-Agent Pipeline</div>
        </div>
        """, unsafe_allow_html=True)

        nav_items = [
            ("📊", "Dashboard", "app.py", "dashboard"),
            ("🔍", "Input Layer", "pages/1_Input.py", "input"),
            ("💼", "Sales Agent", "pages/2_Sales_Agent.py", "sales"),
            ("🤖", "Main Agent", "pages/3_Main_Agent.py", "main"),
            ("⚙️", "Technical Agent", "pages/4_Technical_Agent.py", "technical"),
            ("💰", "Pricing Agent", "pages/5_Pricing_Agent.py", "pricing"),
            ("📄", "Final Report", "pages/6_Final_Report.py", "report"),
        ]

        current = st.session_state.get("current_page", "dashboard")

        for icon, label, page, key in nav_items:
            col = st.container()
            with col:
                clicked = st.button(
                    f"{icon}  {label}",
                    key=f"nav-{key}",
                    use_container_width=True,
                    type="primary"
                )

            if clicked:
                st.session_state.current_page = key
                st.switch_page(page)
