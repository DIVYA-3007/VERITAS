
import re
import pymupdf


def normalize_text(text: str) -> str:
    """
    Clean extracted text while preserving meaningful line breaks.
    """

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[^\S\n]+", " ", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r" +\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def reconstruct_page_text(page) -> str:
    """
    Reconstruct page text using word coordinates.

    Words are grouped by their original text block and line.
    Horizontal gaps are used to determine where spaces belong.
    """

    words = page.get_text("words", sort=True)

    lines = {}

    # Group words by block and line
    for item in words:
        x0, y0, x1, y1, text, block_no, line_no, word_no = item

        line_key = (block_no, line_no)

        if line_key not in lines:
            lines[line_key] = []

        lines[line_key].append({
            "x0": x0,
            "x1": x1,
            "text": text
        })

    reconstructed_lines = []

    # Reconstruct each line
    for line_words in lines.values():

        line_words.sort(key=lambda word: word["x0"])

        reconstructed = ""

        for index, word in enumerate(line_words):

            if index > 0:
                previous_word = line_words[index - 1]

                gap = word["x0"] - previous_word["x1"]

                if gap > 1.0:
                    reconstructed += " "

            reconstructed += word["text"]

        reconstructed_lines.append(reconstructed)

    return "\n".join(reconstructed_lines)


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """
    Extract text page by page from a PDF.

    Returns:
        [
            {
                "page_number": 1,
                "text": "Extracted page content..."
            }
        ]
    """

    extracted_pages = []

    document = pymupdf.open(pdf_path)

    try:
        for page_number, page in enumerate(document, start=1):

            raw_text = reconstruct_page_text(page)

            cleaned_text = normalize_text(raw_text)

            extracted_pages.append({
                "page_number": page_number,
                "text": cleaned_text
            })

    finally:
        document.close()

    return extracted_pages
