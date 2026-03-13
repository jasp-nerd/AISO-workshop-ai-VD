from ddgs import DDGS


def web_search(query: str, max_results: int = 10) -> str:
    """Search the web using DuckDuckGo and return a list of results.

    Use this tool when you need to find up-to-date information from the internet,
    look up facts, find specific web pages, or answer questions requiring current
    knowledge. The results contain only short snippets — to get full page content,
    use the fetch_webpage tool on the most relevant URL.

    If results are not relevant, try calling this tool again with a rephrased query.

    Args:
        query: The search query string. Be specific and include key terms.
        max_results: Number of results to return (default 10, max 20).

    Returns:
        A formatted list of search results with titles, URLs, and snippets.
    """
    max_results = min(max_results, 20)
    results = DDGS().text(query, max_results=max_results)
    if not results:
        return "No search results found. Try rephrasing your query."

    formatted = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "No title")
        url = r.get("href", r.get("link", "No URL"))
        snippet = r.get("body", r.get("snippet", "No snippet"))
        formatted.append(f"{i}. {title}\n   URL: {url}\n   {snippet}")
    return "\n\n".join(formatted)
