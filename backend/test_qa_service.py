
from app.db.database import SessionLocal
from app.services.qa_service import answer_question

db = SessionLocal()

test_questions = [
    "What is the main objective of VERITAS?",
    "Who is the CEO of Microsoft?",
]

try:
    for question in test_questions:

        print("\n" + "=" * 55)
        print("QUESTION:", question)
        print("=" * 55)

        result = answer_question(
            db=db,
            question=question,
            top_k=3,
        )

        print("\nANSWER:")
        print(result["answer"])

        print("\nVERIFIED SOURCES:")

        if result["sources"]:
            for source in result["sources"]:
                print(
                    f"{source['document_name']} | "
                    f"Page {source['page_number']} | "
                    f"Score: {source['similarity_score']}"
                )
        else:
            print("No sufficiently relevant evidence found.")

finally:
    db.close()
