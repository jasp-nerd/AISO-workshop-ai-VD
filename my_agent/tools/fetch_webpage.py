import re

import requests
from bs4 import BeautifulSoup


def fetch_webpage(url: str, search_term: str = "") -> str:
    """Fetch a webpage and return its text content.

    Use this tool to read the full content of a specific URL. Call it:
    - After web_search, to read a page whose snippet looked promising.
    - Directly, when the question provides a URL.

    If the page doesn't contain the answer, try fetching a different URL.

    Args:
        url: The full URL of the webpage to fetch.
        search_term: Optional keyword to focus extraction on. If provided, only
            sections of the page containing this term (with surrounding context)
            will be returned. Use this for very large pages like changelogs or
            documentation where you only need a specific section.

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

    # If a search term is provided, extract only relevant sections
    if search_term:
        term_lower = search_term.lower()
        lines = text.split("\n")
        relevant_chunks = []
        for i, line in enumerate(lines):
            if term_lower in line.lower():
                # Grab surrounding context (30 lines before and after)
                start = max(0, i - 30)
                end = min(len(lines), i + 31)
                chunk = "\n".join(lines[start:end])
                relevant_chunks.append(chunk)
        if relevant_chunks:
            # Deduplicate overlapping chunks
            text = "\n\n---\n\n".join(relevant_chunks)
        # If search_term not found, fall through to return full text

    # Truncate to avoid overwhelming the agent
    if len(text) > 20000:
        text = text[:20000] + "\n\n[Content truncated at 20000 characters...]"
    return text
