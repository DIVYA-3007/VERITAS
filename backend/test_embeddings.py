
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import engine
from app.db.models import DocumentChunk


# Step 1: Load the pretrained embedding model
print("Loading embedding model...")

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2",
    device="cpu"
)


def generate_and_save_embeddings():
    with Session(engine) as session:

        # Step 2: Fetch chunks that don't have embeddings yet
        statement = select(DocumentChunk).where(
            DocumentChunk.embedding.is_(None)
        )

        chunks = session.scalars(statement).all()

        if not chunks:
            print("No chunks found that need embeddings.")
            return

        print(f"Found {len(chunks)} chunks.")

        # Step 3: Extract text from chunks
        texts = [chunk.content for chunk in chunks]

        # Step 4: Convert text into 384-dimensional vectors
        embeddings = model.encode(
            texts,
            normalize_embeddings=True
        )

        # Step 5: Save embeddings into PostgreSQL
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding.tolist()

        session.commit()

        print("Embeddings saved successfully!")

        for chunk in chunks:
            print(
                f"Chunk ID: {chunk.id} | "
                f"Vector dimensions: {len(chunk.embedding)}"
            )


if __name__ == "__main__":
    generate_and_save_embeddings()
    engine.dispose()
