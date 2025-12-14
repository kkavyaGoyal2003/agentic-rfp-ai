import json
import re
from .prompt import SYSTEM_PROMPT, build_user_prompt

def resolve_rfp_metadata(llm_client, parsed_html, source_url, current_date):
    user_prompt = build_user_prompt(parsed_html, source_url, current_date)

    full_prompt = f"""
{SYSTEM_PROMPT}

USER INPUT:
{user_prompt}
"""

    response_text = llm_client.generate(full_prompt)

    # Defensive JSON extraction (LLMs sometimes add text)
    match = re.search(r"\{.*\}", response_text, re.S)
    if not match:
        raise ValueError("LLM did not return valid JSON")

    try:
        metadata = json.loads(match.group())
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON returned by LLM: {e}")

    return metadata
