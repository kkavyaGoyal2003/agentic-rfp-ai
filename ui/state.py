import streamlit as st

def init_state():
    if "urls" not in st.session_state:
        st.session_state.urls = []

    if "events" not in st.session_state:
        st.session_state.events = []

    if "results" not in st.session_state:
        st.session_state.results = None

    if "running" not in st.session_state:
        st.session_state.running = False
        
    if "sales_outputs" not in st.session_state:
        st.session_state.sales_outputs = {}

    if "main_summary" not in st.session_state:
        st.session_state.main_summary = {}

    if "tech_results" not in st.session_state:
        st.session_state.tech_results = {}

    if "pricing_results" not in st.session_state:
        st.session_state.pricing_results = {}
