from bs4 import BeautifulSoup
from typing import Dict, List


def parse_html(html: str) -> Dict:
    """
    Lightweight HTML parsing to extract raw signals.
    No assumptions, no AI, no field mapping.
    """

    soup = BeautifulSoup(html, "html.parser")

    text_blocks = [
        text.strip()
        for text in soup.stripped_strings
        if len(text.strip()) > 2
    ]

    tables = []
    for table in soup.find_all("table"):
        rows = []
        for row in table.find_all("tr"):
            cells = [
                cell.get_text(strip=True)
                for cell in row.find_all(["td", "th"])
            ]
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)

    links = []
    for a in soup.find_all("a", href=True):
        links.append({
            "text": a.get_text(strip=True),
            "href": a["href"]
        })

    return {
        "text_blocks": text_blocks,
        "tables": tables,
        "links": links
    }
