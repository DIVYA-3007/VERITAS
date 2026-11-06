
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.document_service import get_embedding_model


def search_similar_chunks(
    db: Session,
    query: str,
    top_k: int = 5,
) -> list[dict]:

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20.")

    model = get_embedding_model()

    query_embedding = model.encode(
        query.strip(),
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    ).tolist()

    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    statement = (
        select(
            DocumentChunk,
            Document.filename,
            distance.label("distance"),
        )
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .where(
            Document.status == "completed",
            DocumentChunk.embedding.is_not(None),
        )
        .order_by(distance)
        .limit(min(top_k * 10, 100))
    )

    results = db.execute(statement).all()

    unique_results = []
    seen_content = set()

    for chunk, filename, distance_value in results:
        normalized_content = " ".join(chunk.content.lower().split())

        if normalized_content in seen_content:
            continue

        seen_content.add(normalized_content)

        unique_results.append({
            "document_name": filename,
            "chunk_id": str(chunk.id),
            "page_number": chunk.page_number,
            "content": chunk.content,
            "similarity_score": round(
                1 - float(distance_value), 4
            ),
        })

        if len(unique_results) >= top_k:
            break

    return unique_results
