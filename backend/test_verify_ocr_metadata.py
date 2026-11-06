
from uuid import UUID

from sqlalchemy import select

# Import both models to register their relationships.
from app.models.document import Document
from app.models.document_chunk import DocumentChunk

from app.db.database import SessionLocal


DOCUMENT_ID = UUID("6efe2e53-4ce9-46e4-8034-0847a2f7c2dc")


def main():
    db = SessionLocal()

    try:
        statement = (
            select(DocumentChunk)
            .where(
                DocumentChunk.document_id == DOCUMENT_ID
            )
            .order_by(DocumentChunk.chunk_index)
        )

        chunks = db.execute(statement).scalars().all()

        print("\n========== OCR DATABASE VERIFICATION ==========")
        print("Total chunks:", len(chunks))

        for chunk in chunks:

            embedding_dimensions = (
                len(chunk.embedding)
                if chunk.embedding is not None
                else 0
            )

            print("\nChunk:", chunk.chunk_index)
            print("Page:", chunk.page_number)
            print("Extraction method:", chunk.extraction_method)
            print("OCR confidence:", chunk.ocr_confidence)
            print("Embedding dimensions:", embedding_dimensions)
            print("Content length:", len(chunk.content))

        print("\n===============================================")

    finally:
        db.close()


if __name__ == "__main__":
    main()
