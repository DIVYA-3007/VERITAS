
from functools import lru_cache

import easyocr
import numpy as np
import pymupdf


@lru_cache(maxsize=1)
def get_ocr_reader():
    """Load the English OCR model once and reuse it."""
    return easyocr.Reader(["en"], gpu=False)


def extract_page_text_with_ocr(page, dpi: int = 200) -> dict:
    """
    Render a PDF page as an image and extract text using EasyOCR.
    Returns extracted text and average OCR confidence.
    """
    pixmap = page.get_pixmap(
        dpi=dpi,
        colorspace=pymupdf.csRGB,
        alpha=False
    )

    image = np.frombuffer(
        pixmap.samples,
        dtype=np.uint8
    ).reshape(
        pixmap.height,
        pixmap.width,
        3
    )

    reader = get_ocr_reader()

    results = reader.readtext(image)

    extracted_lines = []
    confidence_scores = []

    for result in results:
        text = result[1].strip()
        confidence = float(result[2])

        if text:
            extracted_lines.append(text)
            confidence_scores.append(confidence)

    extracted_text = "\n".join(extracted_lines)

    average_confidence = (
        sum(confidence_scores) / len(confidence_scores)
        if confidence_scores else 0.0
    )

    return {
        "text": extracted_text,
        "confidence": round(average_confidence, 4),
        "method": "ocr"
    }
