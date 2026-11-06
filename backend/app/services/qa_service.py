
from sqlalchemy.orm import Session

from app.services.search_service import search_similar_chunks
from app.services.llm_service import generate_answer


# Initial experimental threshold.
# Calibrate using a larger evaluation dataset.
MIN_SIMILARITY_SCORE = 0.10


def answer_question(
    db: Session,
    question: str,
    top_k: int = 5,
) -> dict:

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    # Step 1: Retrieve candidate evidence
    retrieved_results = search_similar_chunks(
        db=db,
        query=question,
        top_k=top_k,
    )

    # Step 2: Filter weak evidence
    evidence = [
        item
        for item in retrieved_results
        if item["similarity_score"] >= MIN_SIMILARITY_SCORE
    ]

    # Step 3: Abstain when no sufficiently relevant evidence exists
    if not evidence:
        return {
            "question": question,
            "answer": (
                "I could not find sufficiently relevant evidence "
                "in the available documents to answer this question."
            ),
            "sources": [],
            "retrieved_chunks": [],
        }

    # Step 4: Generate an answer using filtered evidence
    answer = generate_answer(
        question=question,
        evidence=evidence,
    )

    # Step 5: Return verified source metadata
    sources = [
        {
            "document_name": item["document_name"],
            "page_number": item["page_number"],
            "chunk_id": item["chunk_id"],
            "similarity_score": item["similarity_score"],
        }
        for item in evidence
    ]

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "retrieved_chunks": evidence,
    }
