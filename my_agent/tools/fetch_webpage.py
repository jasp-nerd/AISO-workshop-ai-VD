import re

import requests
from bs4 import BeautifulSoup


def fetch_webpage(url: str) -> str:
    """Fetch a webpage and return its text content.

    Use this tool to read the full content of a specific URL. Call it:
    - After web_search, to read a page whose snippet looked promising.
    - Directly, when the question provides a URL.

    If the page doesn't contain the answer, try fetching a different URL.

    Args:
        url: The full URL of the webpage to fetch.

    Returns:
        The extracted text content of the webpage.
    """
    response = requests.get(
        url,
        timeout=20,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Remove non-content elements
    for element in soup(
        ["script", "style", "nav", "footer", "header", "aside", "form", "noscript"]
    ):
        element.decompose()

    # Try to find main content area first
    main = soup.find("main") or soup.find("article") or soup.find(role="main")
    target = main if main else soup.body if soup.body else soup

    # Extract text with structure preserved
    text = target.get_text(separator="\n", strip=True)

    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Generous truncation — 20k chars to capture detailed pages
    if len(text) > 20000:
        text = text[:20000] + "\n\n[Content truncated at 20000 characters...]"
    return text
