import os
import pathlib

from google import genai
from google.genai.types import Part


def read_image(file_path: str, question: str) -> str:
    """Analyze an image file and answer a question about it.

    Use this tool when a question references an image file (PNG, JPG, JPEG, WEBP, GIF).
    This tool uses vision capabilities to understand the image content and answer
    your specific question about it.

    Args:
        file_path: The path to the image file (e.g. "benchmark/attachments/14.png").
        question: A specific question to answer about the image. Be detailed about
            what information you need extracted from the image.

    Returns:
        A detailed description and analysis of the image, focused on answering
        the question.
    """
    path = pathlib.Path(file_path)
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    mime_type = mime_types.get(path.suffix.lower(), "image/png")

    image_bytes = path.read_bytes()
    image_part = Part.from_bytes(data=image_bytes, mime_type=mime_type)

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    response = client.models.generate_content(
        model="gemini-3.1-pro-preview",
        contents=[
            image_part,
            f"Analyze this image carefully and answer the following question. "
            f"Be precise and extract all relevant details: {question}",
        ],
    )
    return response.text
