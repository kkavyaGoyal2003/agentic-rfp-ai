SYSTEM_PROMPT = """
You are an AI assistant extracting structured RFP metadata from website content.

STRICT RULES:
- Use ONLY the provided content
- DO NOT hallucinate or infer missing values
- Output VALID JSON ONLY (no markdown, no explanation)
- Dates must be in YYYY-MM-DD format
- If a field is missing or unclear, return null
- Select the most relevant RFP/Tender PDF link only

Required JSON fields:
- tender_reference
- tender_title
- submission_due_date
- pdf_url
"""

def build_user_prompt(parsed_html, source_url, current_date):
    return f"""
Current date: {current_date}
Source URL: {source_url}

TASK:
Extract RFP/Tender metadata.

INSTRUCTIONS:
- Identify the tender reference number
- Identify the tender title
- Identify the submission due date (submission end / bid submission end / deadline)
- Identify the most relevant RFP PDF link from the links section

CONTENT:

TEXT BLOCKS:
{parsed_html['text_blocks']}

TABLES:
{parsed_html['tables']}

LINKS:
{parsed_html['links']}
"""
