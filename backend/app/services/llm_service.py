
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


OLLAMA_API_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2"


def generate_answer(
    question: str,
    evidence: list[dict],
) -> str:

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not evidence:
        return (
            "I could not find relevant evidence in the "
            "available documents to answer this question."
        )

    evidence_context = "\n\n".join(
        [
            (
                f"[Evidence {index}]\n"
                f"Document: {item['document_name']}\n"
                f"Page: {item['page_number']}\n"
                f"Content: {item['content']}"
            )
            for index, item in enumerate(evidence, start=1)
        ]
    )

    system_prompt = """
You are VERITAS, an evidence-grounded document assistant.

STRICT RULES:

1. Answer the user's question directly.
2. Use ONLY the supplied document evidence.
3. Never invent facts or introduce outside knowledge.
4. Do not infer information that is not supported by evidence.
5. If the evidence is insufficient, clearly say so.
6. Keep the answer concise, preferably 2-4 sentences.
7. Avoid repeating the same information.
8. Do NOT generate document citations, page numbers,
   source references, or evidence identifiers.
9. Python will attach verified source references separately.
10. Distinguish directly supported facts from uncertainty.

Return only the answer text.
"""

    user_prompt = f"""
DOCUMENT EVIDENCE:

{evidence_context}

USER QUESTION:

{question}

Provide a concise answer using only the evidence above.
Do not generate citations or page numbers.
"""

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt.strip(),
            },
            {
                "role": "user",
                "content": user_prompt.strip(),
            },
        ],
        "stream": False,
        "options": {
            "temperature": 0.1,
        },
    }

    request = Request(
        OLLAMA_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=180) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

        answer = result["message"]["content"].strip()

        if not answer:
            raise RuntimeError("Ollama returned an empty answer.")

        return answer

    except (URLError, HTTPError, TimeoutError) as exc:
        raise RuntimeError(
            f"Local LLM generation failed: {exc}"
        ) from exc

    except (KeyError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            "Invalid response received from Ollama."
        ) from exc
