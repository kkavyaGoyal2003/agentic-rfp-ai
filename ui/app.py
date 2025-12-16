import streamlit as st
import sys
from pathlib import Path

# 🚨 MUST be the first Streamlit command
st.set_page_config(
    page_title="Agentic RFP AI",
    layout="wide",
)

# ✅ Add project root to PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Safe imports AFTER path fix
from state import init_state
init_state()


st.title("🤖 Agentic RFP Response Automation")
