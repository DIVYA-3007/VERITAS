
def chunk_pages(
    pages: list[dict],
    chunk_size: int = 500,
    overlap: int = 75
) -> list[dict]:
    """
    Split page-wise extracted text into overlapping chunks.

    Each chunk retains its source page number.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")

    chunks = []
    chunk_index = 0

    step = chunk_size - overlap

    for page in pages:

        page_number = page["page_number"]
        text = page["text"].strip()

        if not text:
            continue

        words = text.split()

        for start in range(0, len(words), step):

            end = start + chunk_size
            chunk_words = words[start:end]

            if not chunk_words:
                continue

            chunk_text = " ".join(chunk_words)

            chunks.append({
                "chunk_index": chunk_index,
                "page_number": page_number,
                "content": chunk_text,
                "word_count": len(chunk_words)
            })

            chunk_index += 1

            if end >= len(words):
                break

    return chunks
