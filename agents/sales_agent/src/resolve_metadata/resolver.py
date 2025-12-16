import json
import re
from urllib.parse import urljoin
from .prompt import SYSTEM_PROMPT, build_user_prompt


def resolve_rfp_metadata(llm_client, parsed_html, source_url, current_date):
    """
    LLM is used ONLY to decide WHICH PDF link is the RFP.
    URL is ALWAYS constructed from href (never from LLM text).
    """

    # -------------------------------
    # Step 1: Ask LLM which link is RFP
    # -------------------------------
    user_prompt = build_user_prompt(parsed_html, source_url, current_date)

    full_prompt = f"""
{SYSTEM_PROMPT}

USER INPUT:
{user_prompt}
"""

    response_text = llm_client.generate(full_prompt)

    # Defensive JSON extraction
    match = re.search(r"\{.*\}", response_text, re.S)
    if not match:
        raise ValueError("LLM did not return valid JSON")

    try:
        llm_metadata = json.loads(match.group())
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON returned by LLM: {e}")

    # -------------------------------
    # Step 2: Select PDF link SAFELY
    # -------------------------------
    links = parsed_html.get("links", [])

    pdf_links = [
        link for link in links
        if link.get("href", "").lower().endswith(".pdf")
    ]

    if not pdf_links:
        raise ValueError("No PDF links found in parsed HTML")

    # LLM tells us the NAME/TEXT (not the URL)
    llm_pdf_name = llm_metadata.get("rfp_pdf_name", "").lower()

    selected_pdf = next(
        (l for l in pdf_links if llm_pdf_name in l.get("text", "").lower()),
        pdf_links[0]  # fallback
    )
    raw_href = selected_pdf.get("href", "")
    safe_href = raw_href.replace("\\", "/")


    final_metadata = {
        **llm_metadata,
        "rfp_pdf_name": selected_pdf.get("text"),
        "rfp_pdf_url": urljoin(source_url, safe_href)
    }

    return final_metadata
