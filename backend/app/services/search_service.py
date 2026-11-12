
import re
from threading import Lock

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.document_service import get_embedding_model


# In-memory cache for document chunk embeddings.
# Key: chunk UUID string
# Value: normalized NumPy embedding.
_embedding_cache: dict[str, np.ndarray] = {}

_cache_lock = Lock()


def normalize_content(content: str) -> str:
    """Normalize whitespace for duplicate-content detection."""

    return re.sub(r"\s+", " ", content).strip()


def invalidate_embedding_cache() -> None:
    """Clear cached chunk embeddings after document changes."""

    with _cache_lock:
        _embedding_cache.clear()

    print("[Embedding Cache] Cache invalidated.")


def get_cached_chunk_embeddings(
    rows: list,
    model,
) -> np.ndarray:
    """
    Return cached embeddings where available.

    Generate embeddings only for chunks that are not yet cached.
    """

    embeddings: list[np.ndarray | None] = [None] * len(rows)
    missing_indices = []
    cache_hits = 0

    with _cache_lock:

        # Identify cached and uncached chunks.
        for index, row in enumerate(rows):
            chunk_id = str(row.id)

            cached_embedding = _embedding_cache.get(chunk_id)

            if cached_embedding is not None:
                embeddings[index] = cached_embedding
                cache_hits += 1
            else:
                missing_indices.append(index)

        # Generate embeddings only for missing chunks.
        if missing_indices:
            missing_texts = [
                rows[index].content
                for index in missing_indices
            ]

            generated = model.encode(
                missing_texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )

            for position, index in enumerate(missing_indices):
                embedding = np.asarray(
                    generated[position],
                    dtype=np.float32,
                )

                _embedding_cache[str(rows[index].id)] = embedding
                embeddings[index] = embedding

    print(
        f"[Embedding Cache] Hits: {cache_hits}, "
        f"New embeddings: {len(missing_indices)}, "
        f"Total chunks: {len(rows)}"
    )

    return np.vstack(embeddings)


def search_similar_chunks(
    db: Session,
    query: str,
    top_k: int = 5,
) -> list[dict]:

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20.")

    # Step 1: Fetch text and metadata only.
    # Never select the PostgreSQL vector column.
    statement = (
        select(
            DocumentChunk.id,
            DocumentChunk.document_id,
            DocumentChunk.chunk_index,
            DocumentChunk.page_number,
            DocumentChunk.content,
            Document.filename,
        )
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .where(Document.status == "completed")
        .order_by(
            Document.filename,
            DocumentChunk.page_number,
            DocumentChunk.chunk_index,
        )
    )

    rows = db.execute(statement).all()

    if not rows:
        return []

    # Step 2: Generate query embedding.
    model = get_embedding_model()

    query_embedding = model.encode(
        query.strip(),
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    # Step 3: Reuse cached document embeddings.
    chunk_embeddings = get_cached_chunk_embeddings(
        rows,
        model,
    )

    # Step 4: Calculate cosine similarity.
    similarities = np.dot(
        chunk_embeddings,
        query_embedding,
    )

    # Step 5: Rank highest similarity first.
    ranked_indices = np.argsort(
        -similarities,
        kind="stable",
    )

    # Step 6: Remove exact duplicate passages.
    results = []
    seen_content = set()

    for index in ranked_indices:
        row = rows[index]

        normalized_content = normalize_content(row.content)

        if not normalized_content:
            continue

        if normalized_content in seen_content:
            continue

        seen_content.add(normalized_content)

        results.append(
            {
                "document_name": row.filename,
                "chunk_id": str(row.id),
                "page_number": row.page_number,
                "content": row.content,
                "similarity_score": round(
                    float(
                        np.clip(
                            similarities[index],
                            -1.0,
                            1.0,
                        )
                    ),
                    4,
                ),
            }
        )

        if len(results) >= top_k:
            break

    return results
