from core.llm import OllamaLLM
from agents.sales_agent.src.fetch_html import fetch_html
from agents.sales_agent.src.parse_html import parse_html
from agents.sales_agent.src.resolve_metadata import resolve_rfp_metadata

# ---- CONFIG ----
URL = "https://powergrid-rfp-demo.netlify.app/"
CURRENT_DATE = "2025-07-10"

# ---- INIT LLM CLIENT (COMMON, REUSABLE) ----
llm_client = OllamaLLM(
    model="llama3.2",  # Use exact name: "llama3.2" not "llama3"
    base_url="http://localhost:11434"
)

# ---- STEP 1: Fetch HTML ----
html = fetch_html(URL)
print("\n[STEP 1] HTML fetched")


# ---- STEP 2: Parse HTML ----
parsed = parse_html(html)
print("[STEP 2] HTML parsed")
print(parsed)

# ---- STEP 3: Resolve RFP Metadata (AI) ----
metadata = resolve_rfp_metadata(
    llm_client=llm_client,
    parsed_html=parsed,
    source_url=URL,
    current_date=CURRENT_DATE
)

print("\n[STEP 3] Resolved RFP Metadata:")
print(metadata)