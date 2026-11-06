
from app.db.database import SessionLocal
from app.services.search_service import search_similar_chunks

db = SessionLocal()

try:
    results = search_similar_chunks(
        db,
        "What is this document about?",
        top_k=3
    )

    for index, result in enumerate(results, start=1):
        print(f"\n--- Result {index} ---")
        print("Document:", result["document_name"])
        print("Page:", result["page_number"])
        print("Similarity:", result["similarity_score"])
        print("Content:", result["content"][:180])

    print("\nTotal unique results:", len(results))

finally:
    db.close()
