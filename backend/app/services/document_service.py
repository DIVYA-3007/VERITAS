
from functools import lru_cache
from pathlib import Path
from uuid import uuid4

from sentence_transformers import SentenceTransformer
from sqlalchemy import insert
from sqlalchemy.orm import Session

from ai_engine.document_processing.pdf_extractor import extract_text_from_pdf
from ai_engine.document_processing.text_chunker import chunk_pages

from app.models.document import Document
from app.models.document_chunk import DocumentChunk


EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Load and cache the local embedding model."""

    return SentenceTransformer(
        EMBEDDING_MODEL_NAME,
        device="cpu",
        local_files_only=True,
    )


def process_pdf_document(
    db: Session,
    pdf_path: str | Path,
    original_filename: str,
    file_size: int,
) -> Document:
    """
    Extract and store PDF text and metadata.

    The embedding column is deliberately omitted from SQL INSERT
    statements because PostgreSQL's vector library is blocked
    by the current Windows application-control policy.

    Semantic embeddings are generated in Python during search.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    if file_size <= 0:
        raise ValueError("PDF file cannot be empty.")

    document = Document(
        filename=original_filename,
        file_type="pdf",
        file_size=file_size,
        storage_path=str(pdf_path),
        status="processing",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    document_id = document.id

    try:
        # 1. Extract page-wise text.
        pages = extract_text_from_pdf(str(pdf_path))

        if not pages or not any(page["text"].strip() for page in pages):
            raise ValueError(
                "No extractable text found in PDF, including OCR processing."
            )

        # 2. Generate text chunks.
        chunks = chunk_pages(
            pages,
            chunk_size=500,
            overlap=75,
        )

        if not chunks:
            raise ValueError("No text chunks were generated.")

        # 3. Prepare chunk records without the embedding column.
        chunk_rows = []

        for chunk in chunks:
            chunk_rows.append(
                {
                    "id": uuid4(),
                    "document_id": document_id,
                    "chunk_index": chunk["chunk_index"],
                    "page_number": chunk["page_number"],
                    "content": chunk["content"],
                    "extraction_method": chunk["extraction_method"],
                    "ocr_confidence": chunk["ocr_confidence"],
                }
            )

        # 4. Insert only explicitly supplied columns.
        # The embedding column is completely omitted.
        db.execute(
            insert(DocumentChunk.__table__),
            chunk_rows,
        )

        # 5. Mark document as completed.
        document.status = "completed"

        db.commit()
        db.refresh(document)

        return document

    except Exception:
        db.rollback()

        saved_document = db.get(Document, document_id)

        if saved_document is not None:
            saved_document.status = "failed"
            db.commit()

        raise
