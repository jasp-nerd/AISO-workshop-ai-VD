import re

import requests
from bs4 import BeautifulSoup

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Lines of context to include around each matching line
_CONTEXT_LINES = 15
# Cap on result returned to the model
_MAX_RESULT_CHARS = 4000


def fetch_webpage(url: str, search_term: str) -> str:
    """Fetch a webpage and return its text content.

    Use this tool to read the full content of a specific URL. Call it:
    - After web_search, to read a page whose snippet looked promising.
    - Directly, when the question provides a URL.

    If the page doesn't contain the answer, try fetching a different URL or
    calling this tool again with a more specific search_term.

    Args:
        url: The full URL of the webpage to fetch.
        search_term: The most specific identifier related to the answer — a class
            name, function name, version number, or exact phrase that will appear
            near the answer on the page (e.g. "BaseLabelPropagation", "0.19.1",
            "Other predictors"). Pass "" to get the first 4000 characters of the page.
            When non-empty, the full page text is searched line by line and only the
            lines surrounding each match are returned (up to 4000 chars total).

    Returns:
        The extracted text focused on the relevant section, or the page intro if
        no search_term is given.
    """
    response = requests.get(url, timeout=20, headers=_HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Remove non-content elements
    for element in soup(
        ["script", "style", "nav", "footer", "header", "aside", "form", "noscript"]
    ):
        element.decompose()

    main = soup.find("main") or soup.find("article") or soup.find(role="main")
    target = main if main else soup.body if soup.body else soup
    # Extract full text — no truncation yet, so line-context search covers the
    # entire document regardless of where the term appears
    text = re.sub(r"\n{3,}", "\n\n", target.get_text(separator="\n", strip=True))

    if search_term:
        term_lower = search_term.lower()
        lines = text.split("\n")
        chunks: list[str] = []
        seen_ranges: list[tuple[int, int]] = []

        for i, line in enumerate(lines):
            if term_lower in line.lower():
                start = max(0, i - _CONTEXT_LINES)
                end = min(len(lines), i + _CONTEXT_LINES + 1)
                # Skip if this range overlaps heavily with one already added
                if not any(s <= i <= e for s, e in seen_ranges):
                    chunks.append("\n".join(lines[start:end]))
                    seen_ranges.append((start, end))

        if chunks:
            result = "\n\n---\n\n".join(chunks)
            return result[:_MAX_RESULT_CHARS]

        # Term not found anywhere in the page
        return (
            f"['{search_term}' not found on this page — try a different search_term]\n\n"
            + text[:_MAX_RESULT_CHARS]
        )

    # No search_term — return the opening of the page
    if len(text) > _MAX_RESULT_CHARS:
        text = (
            text[:_MAX_RESULT_CHARS]
            + "\n\n[Content truncated — use search_term to retrieve a specific section]"
        )
    return text
