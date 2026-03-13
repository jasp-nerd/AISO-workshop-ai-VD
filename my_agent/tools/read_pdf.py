import io

import fitz
import requests


def read_pdf(file_path: str) -> str:
    """Read a PDF file and return its full text content.

    Use this tool when a question references a PDF file. Pass the exact file path
    that was provided in the question. This tool also supports URLs to PDF files —
    if the path starts with http:// or https://, it will download and read the PDF.

    Args:
        file_path: The path to the PDF file (e.g. "benchmark/attachments/7.pdf")
            or a URL to a PDF (e.g. "https://example.com/report.pdf").

    Returns:
        The extracted text content of the PDF, with page numbers.
    """
    if file_path.startswith("http://") or file_path.startswith("https://"):
        response = requests.get(
            file_path,
            timeout=30,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        doc = fitz.open(stream=io.BytesIO(response.content), filetype="pdf")
    else:
        doc = fitz.open(file_path)

    text_parts = []
    for i, page in enumerate(doc, 1):
        page_text = page.get_text()
        if page_text.strip():
            text_parts.append(f"--- Page {i} ---\n{page_text}")
    doc.close()
    return "\n".join(text_parts)
