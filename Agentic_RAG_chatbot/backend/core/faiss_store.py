import faiss
import numpy as np
import os
import pickle

class FAISSStore:
    def __init__(self, index_path="faiss_index"):
        self.index_path = index_path
        self.index_file = os.path.join(index_path, "index.faiss")
        self.data_file = os.path.join(index_path, "data.pkl")
        self.index = None
        self.data = []  # stores chunks or response texts
        os.makedirs(index_path, exist_ok=True)
        self._load()

    # -------------------- Load / Save -------------------- #
    def _load(self):
        """Load FAISS index + associated data (if available)."""
        if os.path.exists(self.index_file) and os.path.exists(self.data_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.data_file, "rb") as f:
                self.data = pickle.load(f)
        else:
            self.index = None
            self.data = []

    def _save(self):
        """Persist FAISS index and metadata to disk."""
        if self.index is not None:
            faiss.write_index(self.index, self.index_file)
            with open(self.data_file, "wb") as f:
                pickle.dump(self.data, f)

    # -------------------- Create / Reset -------------------- #
    def create_index(self, chunks):
        """Create a brand-new FAISS index from chunks."""
        embeddings = np.array([c["embedding"] for c in chunks]).astype("float32")
        dim = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        self.data = chunks
        self._save()

    def reset(self):
        """Reset everything — clear FAISS and data."""
        self.index = None
        self.data = []
        if os.path.exists(self.index_file):
            os.remove(self.index_file)
        if os.path.exists(self.data_file):
            os.remove(self.data_file)

    # -------------------- Search -------------------- #
    def search(self, query_embedding, k=3):
        """Find the top-k most similar entries."""
        if self.index is None:
            return []
        D, I = self.index.search(np.array([query_embedding]).astype("float32"), k)
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx < len(self.data):
                item = self.data[idx]
                if isinstance(item, dict):
                    item["similarity"] = float(score)
                else:
                    item = {"text": item, "similarity": float(score)}
                results.append(item)
        return results

    # -------------------- Add New Vector (for caching) -------------------- #
    def add_vector(self, embedding, text):
        """Add a single new text vector (for caching or incremental update)."""
        embedding = np.array([embedding]).astype("float32")

        # Create a new index if not initialized
        if self.index is None:
            dim = embedding.shape[1]
            self.index = faiss.IndexFlatL2(dim)

        self.index.add(embedding)
        self.data.append({"text": text, "embedding": embedding.flatten().tolist()})
        self._save()
