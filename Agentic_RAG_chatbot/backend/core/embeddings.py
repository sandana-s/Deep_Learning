from sentence_transformers import SentenceTransformer
import textwrap

embedder = SentenceTransformer("all-MiniLM-L6-v2")

def chunk_text(text, max_chars=800):
    paragraphs = text.split("\n")
    chunks, current_chunk = [], ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < max_chars:
            current_chunk += para + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def create_embeddings(text: str):
    chunks = chunk_text(text)
    embeddings = embedder.encode(chunks, convert_to_tensor=False)
    return [{"text": c, "embedding": e} for c, e in zip(chunks, embeddings)]

def get_query_embedding(query: str):
    return embedder.encode([query])[0]
