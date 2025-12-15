import streamlit as st
from agents.sales_agent import run_sales_agent
from state import init_state
from components.url_card import render_url_card

st.set_page_config(page_title="Sales Agent", layout="wide")
st.title("🧾 Sales Agent")

init_state()

# ---------------------------
# GUARD
# ---------------------------
if not st.session_state.get("urls"):
    st.info("No URLs submitted yet. Please add URLs from the Input page.")
    st.stop()

# ---------------------------
# RUN BUTTON
# ---------------------------
if st.button("🚀 Run Sales Agent"):
    st.session_state.running = True
    st.session_state.events = []
    st.session_state.results = None

# ---------------------------
# PLACEHOLDERS
# ---------------------------
status_placeholder = st.empty()
final_placeholder = st.empty()

# ---------------------------
# RUN PIPELINE (STREAMING)
# ---------------------------
if st.session_state.running:
    status_placeholder.info("Running Sales Agent...")

    for event in run_sales_agent(urls=st.session_state.urls):
        st.session_state.events.append(event)

        # 🔁 FORCE UI UPDATE
        with status_placeholder.container():
            st.subheader("Live Status")
            for url in st.session_state.urls:
                render_url_card(url, st.session_state.events)

        if event["type"] == "FINAL_RESULT":
            st.session_state.results = event["data"]
            st.session_state.running = False
            break

# ---------------------------
# FINAL OUTPUT
# ---------------------------
if st.session_state.results:
    final_placeholder.divider()
    final_placeholder.subheader("✅ Delivered to Main Agent")

    selected = st.session_state.results["selected_rfp"]
    if not selected:
        final_placeholder.info("No eligible RFP found.")
    else:
        final_placeholder.json(selected)
