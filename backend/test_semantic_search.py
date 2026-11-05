
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import engine
from app.db.models import DocumentChunk


# 1. Load the locally cached embedding model
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2",
    device="cpu",
    local_files_only=True
)


def semantic_search(query: str, limit: int = 5):

    # 2. Convert user question into an embedding
    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    ).tolist()

    # 3. Build the vector similarity query
    statement = (
        select(
            DocumentChunk,
            DocumentChunk.embedding.cosine_distance(
                query_embedding
            ).label("distance")
        )
        .where(DocumentChunk.embedding.is_not(None))
        .order_by("distance")
        .limit(limit)
    )

    # 4. Execute the ORM query
    with Session(engine) as session:
        results = session.execute(statement).all()

        # 5. Display matching chunks
        print(f"\nSearch query: {query}\n")

        for index, (chunk, distance) in enumerate(results, start=1):
            similarity = 1 - distance

            print(f"Result {index}")
            print(f"Content: {chunk.content}")
            print(f"Cosine similarity: {similarity:.4f}")
            print("-" * 50)


if __name__ == "__main__":
    try:
        semantic_search(
            "How does VERITAS find useful information?"
        )
    finally:
        engine.dispose()
