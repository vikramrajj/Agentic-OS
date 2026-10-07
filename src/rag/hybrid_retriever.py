import re
from dataclasses import dataclass
from typing import Any
import numpy as np
from src.core.config import settings
from src.core.logger import logger
from src.rag.knowledge_loader import RunbookDoc, load_knowledge_base


@dataclass
class RetrievalResult:
    doc: RunbookDoc
    score: float
    matched_by: str  # 'dense', 'bm25', 'hybrid'


class HybridRetriever:
    """Combines Dense Vector Retrieval (FAISS) and Sparse Keyword Retrieval (BM25)."""

    def __init__(self, docs: list[RunbookDoc] | None = None):
        self.docs = docs if docs is not None else load_knowledge_base()
        self.encoder = None
        self.faiss_index = None
        self.bm25 = None
        self.tokenized_corpus = []
        self._initialized = False

    def initialize(self):
        """Build FAISS index and BM25 index over documents."""
        if self._initialized or not self.docs:
            return

        logger.info(f"Initializing HybridRetriever with {len(self.docs)} documents...")

        # 1. Initialize BM25
        try:
            from rank_bm25 import BM25Okapi
            self.tokenized_corpus = [
                self._tokenize(doc.searchable_text) for doc in self.docs
            ]
            self.bm25 = BM25Okapi(self.tokenized_corpus)
            logger.info("BM25 index initialized successfully.")
        except ImportError:
            logger.warning("rank_bm25 not installed; sparse search disabled.")

        # 2. Initialize Dense Vector Index (FAISS)
        try:
            import faiss
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading embedding model: {settings.embedding_model}...")
            self.encoder = SentenceTransformer(settings.embedding_model)

            texts = [doc.searchable_text for doc in self.docs]
            embeddings = self.encoder.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

            dimension = embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatIP(dimension)
            self.faiss_index.add(embeddings.astype("float32"))
            logger.info(f"FAISS index built with {self.faiss_index.ntotal} vectors of dimension {dimension}.")
        except Exception as e:
            logger.warning(f"Dense vector indexing failed: {e}. Running BM25-only.")

        self._initialized = True

    def _tokenize(self, text: str) -> list[str]:
        """Simple, robust tokenizer for BM25."""
        return re.findall(r"\b[a-zA-Z0-9_/.-]+\b", text.lower())

    def retrieve(self, query: str, top_k: int = settings.top_k_retrieval) -> list[RetrievalResult]:
        """Retrieve relevant documents using Reciprocal Rank Fusion (RRF)."""
        if not self._initialized:
            self.initialize()

        if not self.docs:
            return []

        dense_ranks: dict[int, int] = {}
        bm25_ranks: dict[int, int] = {}

        # 1. Dense retrieval
        if self.faiss_index and self.encoder:
            try:
                query_vec = self.encoder.encode([query], convert_to_numpy=True, normalize_embeddings=True)
                scores, indices = self.faiss_index.search(query_vec.astype("float32"), min(top_k * 2, len(self.docs)))
                for rank, idx in enumerate(indices[0]):
                    if idx >= 0:
                        dense_ranks[int(idx)] = rank + 1
            except Exception as e:
                logger.error(f"Dense search error: {e}")

        # 2. BM25 retrieval
        if self.bm25:
            try:
                tokens = self._tokenize(query)
                if tokens:
                    bm25_scores = self.bm25.get_scores(tokens)
                    ranked_indices = np.argsort(bm25_scores)[::-1][: top_k * 2]
                    for rank, idx in enumerate(ranked_indices):
                        if bm25_scores[idx] > 0:
                            bm25_ranks[int(idx)] = rank + 1
            except Exception as e:
                logger.error(f"BM25 search error: {e}")

        # 3. Reciprocal Rank Fusion (RRF)
        # RRF Score = 1 / (k + rank)
        rrf_constant = 60
        combined_scores: dict[int, float] = {}
        matched_tags: dict[int, str] = {}

        all_doc_indices = set(dense_ranks.keys()) | set(bm25_ranks.keys())
        for idx in all_doc_indices:
            dense_rank = dense_ranks.get(idx)
            bm25_rank = bm25_ranks.get(idx)

            score = 0.0
            if dense_rank and bm25_rank:
                score = (1.0 / (rrf_constant + dense_rank)) + (1.0 / (rrf_constant + bm25_rank))
                matched_tags[idx] = "hybrid"
            elif dense_rank:
                score = 1.0 / (rrf_constant + dense_rank)
                matched_tags[idx] = "dense"
            elif bm25_rank:
                score = 1.0 / (rrf_constant + bm25_rank)
                matched_tags[idx] = "bm25"

            combined_scores[idx] = score

        # Sort by RRF score descending
        sorted_indices = sorted(combined_scores.keys(), key=lambda i: combined_scores[i], reverse=True)[:top_k]

        results = [
            RetrievalResult(
                doc=self.docs[idx],
                score=combined_scores[idx],
                matched_by=matched_tags[idx]
            )
            for idx in sorted_indices
        ]

        return results


# Global singleton instance
hybrid_retriever = HybridRetriever()
