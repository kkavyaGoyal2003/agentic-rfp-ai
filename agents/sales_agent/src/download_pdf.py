import os
import uuid
import requests
from urllib.parse import urljoin, urlparse
from typing import Optional
from config import DOWNLOADS_DIR


def download_pdf(pdf_url: str, source_url: str) -> Optional[str]:
    """
    Downloads RFP PDF and saves it at project_root/data/downloads
    Returns absolute path of saved PDF or None if failed.
    """
    try:
        # Create downloads directory if it doesn't exist
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)

        # Handle relative URLs
        full_pdf_url = urljoin(source_url, pdf_url)
        
        # Validate URL format
        parsed = urlparse(full_pdf_url)
        if not parsed.scheme or not parsed.netloc:
            print(f"Invalid URL format: {full_pdf_url}")
            return None
        
        # Generate filename
        base_name = os.path.basename(parsed.path) or "rfp.pdf"
        # Remove query parameters from filename
        if '?' in base_name:
            base_name = base_name.split('?')[0]
        # Ensure .pdf extension
        if not base_name.lower().endswith('.pdf'):
            base_name = f"{base_name}.pdf"
        
        unique_id = uuid.uuid4().hex[:8]
        filename = f"rfp_{unique_id}_{base_name}"
        file_path = os.path.join(DOWNLOADS_DIR, filename)

        print(f"Downloading PDF from: {full_pdf_url}")
        
        # Download with timeout and headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(
            full_pdf_url, 
            headers=headers, 
            timeout=30,
            stream=True  # Stream for large files
        )
        response.raise_for_status()
        
        # Check if it's actually a PDF
        content_type = response.headers.get('content-type', '').lower()
        if 'pdf' not in content_type and not full_pdf_url.lower().endswith('.pdf'):
            print(f"Warning: Content-Type is '{content_type}', not PDF")
        
        # Save file
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Verify file was created and has content
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            print(f"PDF saved: {file_path} ({os.path.getsize(file_path)} bytes)")
            return file_path
        else:
            print(f"Failed to save PDF: {file_path}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"Timeout while downloading PDF from: {pdf_url}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"Connection error for PDF URL: {pdf_url}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error {e.response.status_code} for PDF: {pdf_url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request error for PDF {pdf_url}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error downloading PDF {pdf_url}: {e}")
        return None