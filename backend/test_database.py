from sqlalchemy.orm import Session

from app.db.database import engine
from app.db.models import Document, DocumentChunk


def test_document_and_chunks():

    with Session(engine) as session:

        # 1. Create a document
        document = Document(
            filename="veritas_test.pdf",
            file_type="PDF",
            file_size=102400,
            storage_path="storage/uploads/veritas_test.pdf",
        )

        # 2. Create two text chunks
        chunk1 = DocumentChunk(
            chunk_index=0,
            content="VERITAS is a multimodal document intelligence platform."
        )

        chunk2 = DocumentChunk(
            chunk_index=1,
            content="It uses semantic search and evidence-grounded question answering."
        )

        # 3. Connect chunks to the document
        document.chunks.extend([chunk1, chunk2])

        # 4. Save everything
        session.add(document)
        session.commit()

        print("Document and chunks inserted successfully!")
        print("Document ID:", document.id)
        print("Filename:", document.filename)
        print("Number of chunks:", len(document.chunks))


if __name__ == "__main__":
    test_document_and_chunks()
    engine.dispose()
    