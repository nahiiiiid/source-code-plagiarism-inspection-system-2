from typing import Dict, Any
from .preprocess import normalize_code, simple_tokenize
from .fingerprint import winnowing_fingerprints, fingerprint_overlap
from .embeddings import Embedder, cosine, chunk_text, topk_chunk_matches
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class HybridScorer:
    def __init__(self, model_name: str, device: str = "cpu", topk_matches: int = 5):
        self.embedder = Embedder(model_name, device=device)
        self.topk = topk_matches
        self.vectorizer = TfidfVectorizer(ngram_range=(1,3), analyzer='word', min_df=1)

    def score(self, code_a: str, code_b: str) -> Dict[str, Any]:
        # Normalize
        norm_a = normalize_code(code_a)
        norm_b = normalize_code(code_b)

        # Token + fingerprints
        toks_a = simple_tokenize(norm_a)
        toks_b = simple_tokenize(norm_b)
        fp_a = winnowing_fingerprints(toks_a, k=5, window=4)
        fp_b = winnowing_fingerprints(toks_b, k=5, window=4)
        fp_overlap = fingerprint_overlap(fp_a, fp_b)

        # TF-IDF cosine
        X = self.vectorizer.fit_transform([norm_a, norm_b])
        tfidf_cos = float(cosine_similarity(X[0], X[1])[0,0])

        # Embedding (file-level)
        emb_file_a = self.embedder.encode([norm_a])[0]
        emb_file_b = self.embedder.encode([norm_b])[0]
        emb_cos = cosine(emb_file_a, emb_file_b)

        # Chunk-level matches
        chunks_a = chunk_text(norm_a, max_tokens=128, stride=96)
        chunks_b = chunk_text(norm_b, max_tokens=128, stride=96)
        chunk_matches = topk_chunk_matches(chunks_a, chunks_b, self.embedder, topk=self.topk)

        # Ensemble score (weighted)
        # weights can be tuned; start with (embedding 0.6, tfidf 0.25, fp 0.15)
        ensemble = 0.6*emb_cos + 0.25*tfidf_cos + 0.15*fp_overlap

        return {
            "ensemble_score": float(ensemble),
            "components": {
                "embedding_cos": float(emb_cos),
                "tfidf_cos": float(tfidf_cos),
                "fp_overlap": float(fp_overlap),
            },
            "chunks": {
                "a": chunks_a,
                "b": chunks_b,
                "topk_matches": chunk_matches
            }
        }
