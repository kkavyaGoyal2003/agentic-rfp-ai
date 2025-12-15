import streamlit as st
from .progress import render_progress

def render_url_card(url, events):
    st.markdown(f"### 🔗 {url}")

    url_events = [e for e in events if e.get("url") == url]

    if not url_events:
        st.caption("Queued")
        return

    render_progress(url_events)
    st.divider()
