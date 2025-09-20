from __future__ import annotations
from typing import List
import fitz  # PyMuPDF

def ingest_pdf(pdf_path: str, max_pages: int = 20) -> tuple[str, List[bytes]]:
    doc = fitz.open(pdf_path)
    text_parts = []
    images: List[bytes] = []
    for i, page in enumerate(doc):
        if i >= max_pages:
            break
        text_parts.append(page.get_text("text"))
        if i == 0:
            for img in page.get_images(full=True):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                if pix.n >= 5:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                images.append(pix.tobytes("png"))
                break
    return "\n".join(text_parts).strip(), images[:1]
