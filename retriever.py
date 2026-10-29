"""
retriever.py - Step 2 of RAG: find the chunks that best match a question.

We use TF-IDF + cosine similarity (the same idea you used in HelpDesk projects).
It works fully offline, needs no GPU, and is easy to explain in interviews.

Upgrade idea: replace TF-IDF with sentence embeddings
(e.g. sentence-transformers "all-MiniLM-L6-v2") + a vector store like FAISS
or ChromaDB. The rest of the app stays the same.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from pdf_utils import Chunk


class TfidfRetriever:
    def __init__(self, chunks: list[Chunk]):
        if not chunks:
            raise ValueError("No text found. Is the PDF a scanned image?")
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),   # single words + two-word phrases
            sublinear_tf=True,
        )
        self.matrix = self.vectorizer.fit_transform([c.text for c in chunks])

    def search(self, question: str, top_k: int = 4) -> list[tuple[Chunk, float]]:
        """Return the top_k chunks with their similarity score (0 to 1)."""
        q_vec = self.vectorizer.transform([question])
        scores = cosine_similarity(q_vec, self.matrix)[0]
        best = scores.argsort()[::-1][:top_k]
        return [(self.chunks[i], float(scores[i])) for i in best if scores[i] > 0]
