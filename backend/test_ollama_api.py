
import json
from urllib.request import Request, urlopen

url = "http://localhost:11434/api/chat"

payload = {
    "model": "llama3.2",
    "messages": [
        {
            "role": "system",
            "content": (
                "You are VERITAS, an evidence-grounded document "
                "assistant. Answer directly using only the supplied "
                "evidence. Cite the source page. Do not invent facts."
            )
        },
        {
            "role": "user",
            "content": (
                "Evidence: [Page 1] VERITAS is designed to extract, "
                "organize, and retrieve information from digital "
                "documents.\n\n"
                "Question: What is the main objective of VERITAS?"
            )
        }
    ],
    "stream": False,
    "options": {
        "temperature": 0.1
    }
}

request = Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)

try:
    with urlopen(request, timeout=180) as response:
        result = json.loads(response.read().decode("utf-8"))

    print("\nVERITAS LOCAL LLM TEST")
    print("----------------------")
    print("Model:", result.get("model"))
    print("Answer:")
    print(result["message"]["content"])

except Exception as error:
    print("Ollama API test failed:", error)
