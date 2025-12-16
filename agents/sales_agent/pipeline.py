import os
import sys
from datetime import datetime, timedelta

project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from agents.sales_agent.src.fetch_html import fetch_html
from agents.sales_agent.src.parse_html import parse_html
from agents.sales_agent.src.resolve_metadata import resolve_rfp_metadata
from agents.sales_agent.src.resolve_metadata.normalize_metadata import normalize_metadata
from agents.sales_agent.src.download_pdf import download_pdf
from core.llm import OllamaLLM


# ---- CONFIG ----
BASE_DIR = os.path.dirname(__file__)
URLS_FILE = os.path.join(BASE_DIR, "urls.txt")
CURRENT_DATE = datetime.today().strftime("%Y-%m-%d")


def load_urls(file_path: str) -> list[str]:
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def is_within_next_3_months(due_date_str: str, current_date_str: str) -> bool:
    if not due_date_str:
        return False

    current_date = datetime.strptime(current_date_str, "%Y-%m-%d")
    max_date = current_date + timedelta(days=90)

    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
    except ValueError:
        return False

    return current_date <= due_date <= max_date


def get_rfp(start_date=None, urls=None):
    """
    Generator-based Sales Agent pipeline.
    Yields progress events and a final result.
    """
    if not start_date:
        start_date = CURRENT_DATE

    llm_client = OllamaLLM(
        model="llama3.2",
        base_url="http://localhost:11434"
    )

    # ---- Load URLs ----
    if urls:
        url_list = urls
    else:
        url_list = load_urls(URLS_FILE)

    url_results = []

    # ---- PER-URL PIPELINE ----
    for url in url_list:
        url_state = {
            "url": url,
            "stages": {
                "fetching": {"status": "pending"},
                "summarizing": {"status": "pending"}
            },
            "metadata": None,
            "status": "PENDING"
        }

        # QUEUED
        yield {
            "type": "STATUS",
            "url": url,
            "stage": "QUEUED",
            "state": url_state
        }

        try:
            # FETCHING
            url_state["stages"]["fetching"]["status"] = "running"
            yield {
                "type": "STATUS",
                "url": url,
                "stage": "FETCHING",
                "status": "RUNNING"
            }

            html = fetch_html(url)
            parsed = parse_html(html)
            
            pdf_href = None
            for link in parsed.get("links", []):
                href = link.get("href", "")
                if href.lower().endswith(".pdf"):
                    pdf_href = href
                    break


            url_state["stages"]["fetching"]["status"] = "done"
            yield {
                "type": "STATUS",
                "url": url,
                "stage": "FETCHING",
                "status": "DONE"
            }

            # SUMMARIZING
            url_state["stages"]["summarizing"]["status"] = "running"
            yield {
                "type": "STATUS",
                "url": url,
                "stage": "SUMMARIZING",
                "status": "RUNNING"
            }

            raw_metadata = resolve_rfp_metadata(
                llm_client=llm_client,
                parsed_html=parsed,
                source_url=url,
                current_date=start_date
            )

            metadata = normalize_metadata(raw_metadata, url)
            if pdf_href:
                metadata["pdf_url"] = pdf_href


            url_state["stages"]["summarizing"]["status"] = "done"
            url_state["metadata"] = metadata
            url_state["status"] = "SUMMARIZED"

            yield {
                "type": "STATUS",
                "url": url,
                "stage": "SUMMARIZING",
                "status": "DONE",
                "metadata": metadata
            }

        except Exception as e:
            url_state["status"] = "ERROR"
            url_state["error"] = str(e)

            yield {
                "type": "STATUS",
                "url": url,
                "stage": "ERROR",
                "error": str(e)
            }

        url_results.append(url_state)

    # ---- GLOBAL FILTERING ----
    filtered_rfps = []
    for item in url_results:
        metadata = item.get("metadata")

        if not metadata:
            item["status"] = "FAILED"
            continue

        if is_within_next_3_months(
            metadata.get("submission_due_date"),
            start_date
        ):
            item["status"] = "FILTERED"
            filtered_rfps.append(item)
            yield {
                "type": "STATUS",
                "url": item["url"],
                "stage": "FILTERED",
                "status": "ACCEPTED"
            }
        else:
            item["status"] = "SKIPPED"
            yield {
                "type": "STATUS",
                "url": item["url"],
                "stage": "FILTERED",
                "status": "SKIPPED"
            }

    # ---- SELECT ONE RFP ----
    if not filtered_rfps:
        yield {
            "type": "FINAL_RESULT",
            "data": {
                "urls": url_results,
                "selected_rfp": None
            }
        }
        return

    selected_item = filtered_rfps[-1]
    selected_rfp = selected_item["metadata"]

    # ---- DELIVERY ----
    yield {
        "type": "STATUS",
        "url": selected_item["url"],
        "stage": "DELIVERY",
        "status": "RUNNING"
    }

    pdf_path = download_pdf(
        pdf_url=selected_rfp["pdf_url"],
        source_url=selected_rfp["source_url"]
    )

    selected_rfp["rfp_pdf_path"] = pdf_path
    selected_item["status"] = "DELIVERED"

    yield {
        "type": "STATUS",
        "url": selected_item["url"],
        "stage": "DELIVERY",
        "status": "DONE",
        "pdf_path": pdf_path
    }

    # ---- FINAL RESULT ----
    yield {
        "type": "FINAL_RESULT",
        "data": {
            "urls": url_results,
            "selected_rfp": selected_rfp
        }
    }
