import streamlit as st
import time
import inspect
import os

from agents.sales_agent.pipeline import get_rfp

URLS_FILE = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "agents",
        "sales_agent",
        "urls.txt"
    )
)


def _is_fresh_valid_pdf(path: str, run_start_time: float) -> bool:
    """
    Strict validation:
    - path exists
    - is file
    - size > 0
    - modified AFTER this run started
    """
    if not isinstance(path, str):
        return False

    if not os.path.isfile(path):
        return False

    if os.path.getsize(path) <= 0:
        return False

    modified_time = os.path.getmtime(path)
    return modified_time >= run_start_time


def start_sales_agent(url: str):
    run_start_time = time.time()

    st.session_state.url_status[url]["stage"] = "Processing"
    st.session_state.url_status[url]["history"].append(
        ("Started", run_start_time)
    )

    # ---- BACKUP urls.txt ----
    original_urls = ""
    if os.path.exists(URLS_FILE):
        with open(URLS_FILE, "r") as f:
            original_urls = f.read()

    try:
        # ---- WRITE ONLY CURRENT URL ----
        with open(URLS_FILE, "w") as f:
            f.write(url.strip() + "\n")

        # ---- CALL BACKEND ----
        sig = inspect.signature(get_rfp)
        result = get_rfp() if len(sig.parameters) == 0 else get_rfp(None)

        # =====================================================
        # CASE 1: SKIPPED (VALID BUSINESS OUTCOME)
        # =====================================================
        if not result:
            st.session_state.url_status[url]["stage"] = "Skipped (Not Eligible)"
            st.session_state.url_status[url]["history"].append(
                ("Skipped (no valid RFP)", time.time())
            )
            return

        # =====================================================
        # CASE 2: PDF DOWNLOAD FAILED / STALE FILE
        # =====================================================
        pdf_path = result.get("rfp_pdf_path") if isinstance(result, dict) else None

        if not _is_fresh_valid_pdf(pdf_path, run_start_time):
            st.session_state.url_status[url]["stage"] = "Failed (PDF download error)"
            st.session_state.url_status[url]["history"].append(
                ("PDF download failed or stale file", time.time())
            )
            return

        # =====================================================
        # CASE 3: SUCCESS
        # =====================================================
        st.session_state.sales_outputs[url] = result
        st.session_state.url_status[url]["stage"] = "Delivered to Main Agent"
        st.session_state.url_status[url]["history"].append(
            ("Completed", time.time())
        )

    except Exception as e:
        st.session_state.url_status[url]["stage"] = "Error"
        st.session_state.url_status[url]["error"] = str(e)
        st.session_state.url_status[url]["history"].append(
            ("Error", time.time())
        )

    finally:
        # ---- RESTORE urls.txt ----
        with open(URLS_FILE, "w") as f:
            f.write(original_urls)


def retry_url(url: str):
    st.session_state.url_status[url] = {
        "stage": "Queued",
        "history": []
    }
