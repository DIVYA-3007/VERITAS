
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from ai_engine.document_processing.pdf_extractor import extract_text_from_pdf


PDF_PATH = PROJECT_ROOT / "sample.pdf"


def test_pdf_extraction():

    if not PDF_PATH.exists():
        print("PDF not found:", PDF_PATH)
        return

    pages = extract_text_from_pdf(str(PDF_PATH))

    print("\nPDF EXTRACTION TEST")
    print("Total pages:", len(pages))

    for page in pages:

        page_number = page["page_number"]
        text = page["text"]

        print("\n" + "=" * 60)
        print("PAGE:", page_number)
        print("=" * 60)

        print(text)

        if page_number == 1:

            print("\nEXACT SPACING DIAGNOSTICS")

            position = text.find("platform")

            print(
                "Correct phrase found:",
                "platform designed" in text
            )

            print(
                "Joined phrase found:",
                "platformdesigned" in text
            )

            if position != -1:
                print(
                    "Exact text:",
                    repr(text[position - 15:position + 50])
                )

            print(
                "Extracted character count:",
                len(text)
            )


if __name__ == "__main__":
    test_pdf_extraction()
