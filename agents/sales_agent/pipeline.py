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


def get_rfp(start_date):
    if not start_date:
        start_date = CURRENT_DATE
    llm_client = OllamaLLM(
        model="llama3.2",
        base_url="http://localhost:11434"
    )

    urls = load_urls(URLS_FILE)
    collected_rfps = []

    for url in urls:
        print(f"\n--- Processing URL: {url} ---")

        # STEP 1: Fetch HTML
        html = fetch_html(url)

        # STEP 2: Parse HTML
        parsed = parse_html(html)

        # STEP 3: Resolve metadata (LLM)
        raw_metadata = resolve_rfp_metadata(
            llm_client=llm_client,
            parsed_html=parsed,
            source_url=url,
            current_date=start_date
        )

        # STEP 4: Normalize metadata
        metadata = normalize_metadata(raw_metadata, url)

        # STEP 5: Filter (next 3 months)
        if not is_within_next_3_months(
            metadata.get("submission_due_date"),
            start_date
        ):
            print("Skipped (not due in next 3 months)")
            continue

        collected_rfps.append(metadata)
        print("Accepted RFP:", metadata.get("tender_reference"))

    # ---- DOWNLOAD ONLY THE LAST SELECTED RFP ----
    if not collected_rfps:
        print("\nNo RFPs selected.")
        return []

    selected_rfp = collected_rfps[-1]
    print("\nDownloading selected RFP PDF...")

    pdf_path = download_pdf(
        pdf_url=selected_rfp["pdf_url"],
        source_url=selected_rfp["source_url"]
    )

    selected_rfp["rfp_pdf_path"] = pdf_path

    return selected_rfp


if __name__ == "__main__":
    selected_rfp = get_rfp()
    print(selected_rfp)

