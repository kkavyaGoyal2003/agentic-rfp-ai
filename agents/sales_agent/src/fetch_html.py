import requests
from typing import Optional


class HTMLFetchError(Exception):
    pass


def fetch_html(url: str, timeout: int = 15) -> str:
    """
    Fetch raw HTML content from a given URL.

    Args:
        url (str): Tender page URL
        timeout (int): Request timeout in seconds

    Returns:
        str: Raw HTML content

    Raises:
        HTMLFetchError: If request fails or returns non-200
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
    except requests.RequestException as e:
        raise HTMLFetchError(f"Failed to fetch URL: {url}") from e

    if response.status_code != 200:
        raise HTMLFetchError(
            f"Non-200 status code {response.status_code} for URL: {url}"
        )

    return response.text
