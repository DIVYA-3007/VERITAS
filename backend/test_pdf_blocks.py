
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pymupdf

PDF_PATH = PROJECT_ROOT / "sample.pdf"


def reconstruct_page_text(page):
    words = page.get_text("words", sort=True)
    lines = {}

    for item in words:
        x0, y0, x1, y1, text, block_no, line_no, word_no = item
        line_key = (block_no, line_no)

        lines.setdefault(line_key, []).append({
            "x0": x0,
            "x1": x1,
            "text": text
        })

    reconstructed_lines = []

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


def test_pdf_reconstruction():
    if not PDF_PATH.exists():
        print("PDF not found:", PDF_PATH)
        return

    document = pymupdf.open(PDF_PATH)

    try:
        for page_number, page in enumerate(document, start=1):
            text = reconstruct_page_text(page)

            print("\nPAGE:", page_number)

            if page_number == 1:
                target = "platform designed"

                print("Target:", repr(target))
                print("Found:", target in text)

                position = text.find("platform")

                if position != -1:
                    print(
                        "Exact extracted text:",
                        repr(text[position - 15:position + 40])
                    )

                    print(
                        "Character codes:",
                        [ord(char) for char in text[position:position + 20]]
                    )

            print("\nExtracted text:")
            print(text)

    finally:
        document.close()


if __name__ == "__main__":
    test_pdf_reconstruction()
