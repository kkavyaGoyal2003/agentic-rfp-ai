from fetch_html import fetch_html
from parse_html import parse_html

url = "https://powergrid-rfp-demo.netlify.app/"
html = fetch_html(url)
parsed = parse_html(html)

print("Sample Text:", parsed["text_blocks"])
print("PDF Links:", [l for l in parsed["links"] if ".pdf" in l["href"].lower()])
