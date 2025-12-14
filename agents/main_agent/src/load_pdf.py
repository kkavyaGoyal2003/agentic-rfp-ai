import os
import pdfplumber


def load_rfp_pdf(rfp_pdf_path: str) -> dict:
    """
    Loads an RFP PDF and extracts all textual content.
    Works for text-based PDFs with tables and logos.
    Images (logos) are ignored automatically.
    """

    if not os.path.exists(rfp_pdf_path):
        raise FileNotFoundError(f"RFP PDF not found at: {rfp_pdf_path}")

    extracted_text = []

    with pdfplumber.open(rfp_pdf_path) as pdf:
        total_pages = len(pdf.pages)

        for page in pdf.pages:
            # Simpler, more reliable extraction for text-based PDFs
            text = page.extract_text()

            if text and text.strip():
                extracted_text.append(text)

    full_text = "\n".join(extracted_text)

    return {
        "rfp_pdf_path": rfp_pdf_path,
        "num_pages": total_pages,
        "text_preview": full_text[:500],
        "full_text": full_text
    }
