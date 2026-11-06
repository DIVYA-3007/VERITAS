
from app.services.llm_service import generate_answer

question = "What is the main objective of VERITAS?"

evidence = [
    {
        "document_name": "sample.pdf",
        "page_number": 1,
        "content": (
            "VERITAS is a prototype document intelligence "
            "platform designed to extract, organize, and "
            "retrieve information from digital documents. "
            "It combines document processing, semantic "
            "embeddings, vector search, and evidence-grounded "
            "question answering."
        ),
    }
]

answer = generate_answer(
    question=question,
    evidence=evidence,
)

print("\nVERITAS LLM SERVICE TEST")
print("------------------------")
print("Question:", question)
print("\nGenerated Answer:")
print(answer)
