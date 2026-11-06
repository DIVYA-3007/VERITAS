
from functools import lru_cache
from pathlib import Path

from sentence_transformers import SentenceTransformer
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
    Extract, chunk, embed, and store a PDF document.

    Stores page number, extraction method, OCR confidence,
    and vector embeddings for every generated chunk.
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
        # 1. Extract page-wise text using native extraction or OCR.
        pages = extract_text_from_pdf(str(pdf_path))

        if not pages or not any(page["text"].strip() for page in pages):
            raise ValueError(
                "No extractable text found in PDF, including OCR processing."
            )

        # 2. Split extracted text into chunks.
        chunks = chunk_pages(
            pages,
            chunk_size=500,
            overlap=75,
        )

        if not chunks:
            raise ValueError("No text chunks were generated.")

        # 3. Generate embeddings.
        model = get_embedding_model()

        texts = [chunk["content"] for chunk in chunks]

        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        if embeddings.shape[1] != EMBEDDING_DIMENSION:
            raise ValueError("Unexpected embedding dimension.")

        if len(embeddings) != len(chunks):
            raise ValueError("Embedding count does not match chunk count.")

        # 4. Save chunks, embeddings, and extraction metadata.
        document_chunks = []

        for chunk, embedding in zip(chunks, embeddings):

            document_chunks.append(
                DocumentChunk(
                    document_id=document_id,
                    chunk_index=chunk["chunk_index"],
                    page_number=chunk["page_number"],
                    content=chunk["content"],
                    extraction_method=chunk["extraction_method"],
                    ocr_confidence=chunk["ocr_confidence"],
                    embedding=embedding.tolist(),
                )
            )

        db.add_all(document_chunks)

        # 5. Mark document as successfully processed.
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
