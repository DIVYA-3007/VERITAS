
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from ai_engine.document_processing.pdf_extractor import extract_text_from_pdf
from ai_engine.document_processing.text_chunker import chunk_pages


PDF_PATH = PROJECT_ROOT / "sample.pdf"


def test_text_chunking():

    # 1. Extract text from the PDF
    pages = extract_text_from_pdf(str(PDF_PATH))

    print("Total PDF pages:", len(pages))

    # 2. Split extracted text into chunks
    chunks = chunk_pages(
        pages,
        chunk_size=100,
        overlap=20
    )

    print("Total chunks generated:", len(chunks))

    # 3. Display each chunk
    for chunk in chunks:

        print("\n" + "=" * 60)
        print("Chunk index:", chunk["chunk_index"])
        print("Source page:", chunk["page_number"])
        print("Word count:", chunk["word_count"])
        print("=" * 60)

        print(chunk["content"])


if __name__ == "__main__":
    test_text_chunking()
