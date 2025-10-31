import asyncio
import httpx
import hashlib
import json
from functools import lru_cache
from backend.core.faiss_store import FAISSStore
from backend.core.embeddings import get_query_embedding
import numpy as np

class LLMClient:
    """
    Optimized Ollama client:
    ✅ Persistent connection
    ✅ Local + FAISS cache
    ✅ Robust retry logic
    ✅ Works with streaming JSON responses
    """

    def __init__(self, model_name="gemma2:2b", use_faiss_cache=True):
        self.model_name = model_name
        self.api_url = "http://localhost:11434/api/generate"
        self._client = None
        self._is_warmed_up = False
        self.use_faiss_cache = use_faiss_cache
        self.response_cache = {}
        self.faiss_cache = FAISSStore("faiss_cache") if use_faiss_cache else None

    # ------------------------------------------------------------
    async def _get_client(self):
        """Ensure one persistent async client for all HTTP calls."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(120))
        return self._client

    # ------------------------------------------------------------
    async def warm_up(self):
        """Preload the model once when FastAPI starts."""
        if not self._is_warmed_up:
            print(f"⚙️ Warming up {self.model_name} model...")
            try:
                resp = await self.generate("Hello! This is a warm-up prompt.")
                if not resp.startswith("⚠️ Error"):
                    self._is_warmed_up = True
                    print("✅ Model warm-up complete.")
                else:
                    raise RuntimeError(resp)
            except Exception as e:
                print(f"⚠️ Warm-up failed: {e}")

    # ------------------------------------------------------------
    @staticmethod
    @lru_cache(maxsize=200)
    def _hash_prompt(system_prompt: str, prompt: str):
        """Hash the combined prompt for consistent cache keys."""
        key = f"{system_prompt}:{prompt}"
        return hashlib.sha256(key.encode()).hexdigest()

    # ------------------------------------------------------------
    def _safe_embedding(self, text: str):
        """Safely extract the embedding vector from get_query_embedding()."""
        emb = get_query_embedding(text)
        # Normalize and validate
        if emb is None:
            raise ValueError("get_query_embedding() returned None")
        
        # accept numpy arrays
        if isinstance(emb,np.ndarray):
            return emb.tolist()
        if isinstance(emb, (list, tuple)):
            # handle [[...]] or ( [...], )
            if len(emb) == 0:
                raise ValueError("get_query_embedding() returned empty list/tuple")
            if isinstance(emb[0], (list, tuple)):
                return emb[0]  # normal case: [[vector]]
            return emb        # already a vector
        raise TypeError(f"Unexpected embedding type: {type(emb)}")

    # ------------------------------------------------------------
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        Generate response via Ollama, with caching and retry logic.
        """
        full_prompt = f"{system_prompt}\n\nUser Query:\n{prompt}".strip()
        key = self._hash_prompt(system_prompt, prompt)

        # 🔹 1. Check local cache first
        if key in self.response_cache:
            print("⚡ Using cached response (local dict)")
            return self.response_cache[key]

        # 🔹 2. Check FAISS semantic cache
        if self.use_faiss_cache and self.faiss_cache.index is not None:
            try:
                query_embedding = self._safe_embedding(prompt)
                similar_chunks = self.faiss_cache.search(query_embedding, k=1)
                if similar_chunks:
                    result_text = similar_chunks[0].get("text")
                    if result_text:
                        print("🧠 Using FAISS semantic cache")
                        return result_text
            except Exception as e:
                print(f"⚠️ FAISS cache skipped due to error: {e}")

        # 🔹 3. Prepare payload for Ollama
        max_tokens = 16 if "summarize" not in prompt.lower() else 64
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": True,
            "num_predict": max_tokens,
            "temperature": 0.3,
        }

        # 🔹 4. Try up to 3 times
        for attempt in range(3):
            try:
                client = await self._get_client()
                async with client.stream("POST", self.api_url, json=payload) as response:
                    response.raise_for_status()
                    result_text = ""

                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            data = json.loads(line)
                            chunk = data.get("response", "")
                            result_text += chunk
                        except json.JSONDecodeError:
                            continue

                    result_text = result_text.strip()
                    if not result_text:
                        raise ValueError("Empty response from Ollama stream.")

                    # Save to caches
                    self.response_cache[key] = result_text
                    if self.use_faiss_cache:
                        try:
                            emb = self._safe_embedding(prompt)
                            self.faiss_cache.add_vector(emb, result_text)
                        except Exception as e:
                            print(f"⚠️ Skipping FAISS add_vector due to: {e}")

                    return result_text

            except Exception as e:
                print(f"⚠️ Ollama error (attempt {attempt + 1}/3): {e}")
                await asyncio.sleep(2)

        return "⚠️ Error: Ollama not responding. Please ensure `ollama serve` is running and the model is pulled."

    # ------------------------------------------------------------
    async def close(self):
        """Gracefully close async client."""
        if self._client:
            await self._client.aclose()


# ✅ Shared instance for use across agents
llm_client = LLMClient(model_name="gemma2:2b",use_faiss_cache=False)
