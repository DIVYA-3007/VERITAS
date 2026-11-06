
from pathlib import Path

from app.db.database import SessionLocal
from app.services.document_service import process_pdf_document


def main():
    pdf_path = Path("scanned_test.pdf").resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    db = SessionLocal()

    try:
        document = process_pdf_document(
            db=db,
            pdf_path=pdf_path,
            original_filename="scanned_test.pdf",
            file_size=pdf_path.stat().st_size,
        )

        print("\n========== INGESTION RESULT ==========")
        print("Document ID:", document.id)
        print("Filename:", document.filename)
        print("Status:", document.status)
        print("Ingestion successful!")
        print("======================================")

    finally:
        db.close()


if __name__ == "__main__":
    main()
