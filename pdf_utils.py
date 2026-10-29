"""
pdf_utils.py - Step 1 of RAG: read PDFs and cut the text into small chunks.

Why chunks? An LLM can't read a 300-page book in one go, and even if it could,
it would be slow and expensive. So we split the text into small pieces and
later send only the few pieces that match the user's question.
"""

import re
from dataclasses import dataclass

from pypdf import PdfReader


@dataclass
class Chunk:
    text: str
    source: str  # file name
    page: int    # 1-based page number


def extract_pages(file, file_name: str) -> list[tuple[int, str]]:
    """Return a list of (page_number, text) for one PDF."""
    reader = PdfReader(file)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = re.sub(r"\s+", " ", text).strip()  # clean extra spaces/newlines
        if text:
            pages.append((i, text))
    return pages


def split_into_chunks(
    pages: list[tuple[int, str]],
    file_name: str,
    chunk_size: int = 500,
    overlap: int = 100,
) -> list[Chunk]:
    """
    Split each page into overlapping chunks of about `chunk_size` characters.
    The overlap makes sure a sentence cut at the edge of one chunk still
    appears whole in the next chunk.
    """
    chunks = []
    for page_no, text in pages:
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            # try to end the chunk at a full stop so sentences stay whole
            if end < len(text):
                last_dot = text.rfind(". ", start, end)
                if last_dot > start + chunk_size // 2:
                    end = last_dot + 1
            piece = text[start:end].strip()
            if piece:
                chunks.append(Chunk(text=piece, source=file_name, page=page_no))
            if end >= len(text):
                break
            # move forward, but step back by `overlap` characters
            start = end - overlap if end - overlap > start else end
            # don't start a chunk in the middle of a word
            space = text.find(" ", start, end)
            if 0 < start < len(text) and text[start - 1] != " " and space != -1:
                start = space + 1
    return chunks


def load_pdf_chunks(file, file_name: str) -> list[Chunk]:
    """Read one PDF and return all its chunks."""
    pages = extract_pages(file, file_name)
    return split_into_chunks(pages, file_name)
