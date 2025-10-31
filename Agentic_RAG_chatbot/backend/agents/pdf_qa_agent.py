from backend.core.faiss_store import FAISSStore
from backend.core.embeddings import get_query_embedding
from backend.core.llm_clients import llm_client


class PDFQAAgent:
    """
    Agent responsible for answering user queries based on uploaded PDFs.
    Uses FAISS for context retrieval and Ollama for generative response.
    """

    def __init__(self, faiss_store: FAISSStore):
        self.faiss_store = faiss_store
        self.name = "PDF Q&A Agent"

    async def process(self, query: str, k: int = 3) -> str:
        """Process a question and return an answer using RAG pipeline."""

        try:
            # 1️⃣ Embed the query
            query_embedding = get_query_embedding(query)

            # 2️⃣ Retrieve relevant document chunks
            relevant_chunks = self.faiss_store.search(query_embedding, k=k)

            if not relevant_chunks:
                return "I couldn't find any relevant context in the document."

            # 3️⃣ Construct context and prompts
            context = "\n\n".join([
                chunk["text"] if isinstance(chunk, dict) and "text" in chunk else str(chunk)
                for chunk in relevant_chunks])

            system_prompt = """You are a helpful AI assistant that answers questions based on a provided document context.
You should:
1. Understand the question deeply and carefully
2. Keep responses short (2–3 sentences max)
3. Give a comprehensive, natural, conversational answer
4. DO NOT just copy sentences from the context and Do not include explanations or introductions
5. Explain ideas clearly, in your own words
6. If context is ambiguous, clearly mention your reasoning
7. Be natural and fluent like ChatGPT."""

            prompt = f"""Based on the following context from the document, answer the question clearly and conversationally.

Context:
{context}

Question: {query}

Answer:"""

            # 4️⃣ Generate response from Ollama
            response = await llm_client.generate(prompt=prompt, system_prompt=system_prompt)

            if not response or len(response.strip()) == 0:
                return "I couldn’t generate a response. Please rephrase your question."

            return response.strip()

        except Exception as e:
            return f"⚠️ Error: {str(e)}. Ensure Ollama is running via 'ollama serve' and a model like 'llama3' is pulled."
