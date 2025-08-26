from typing import List, Dict, Any
import numpy as np
import torch
from sentence_transformers import SentenceTransformer, util

class Embedder:
    def __init__(self, model_name: str, device: str = "cpu"):
        self.model = SentenceTransformer(model_name, device=device)
    def encode(self, texts: List[str]):
        return self.model.encode(texts, convert_to_tensor=True, show_progress_bar=False)

def cosine(u, v) -> float:
    if isinstance(u, np.ndarray):
        u = torch.tensor(u)
    if isinstance(v, np.ndarray):
        v = torch.tensor(v)
    return float(util.cos_sim(u, v).item())

def chunk_text(text: str, max_tokens: int = 128, stride: int = 96) -> List[str]:
    # token-agnostic sliding window on whitespace tokens
    toks = text.split()
    chunks = []
    i = 0
    while i < len(toks):
        chunk = toks[i:i+max_tokens]
        if not chunk:
            break
        chunks.append(" ".join(chunk))
        if i + max_tokens >= len(toks):
            break
        i += stride
    if not chunks:
        chunks = [text]
    return chunks

def topk_chunk_matches(chunks1: List[str], chunks2: List[str], embedder: Embedder, topk: int = 5):
    e1 = embedder.encode(chunks1)
    e2 = embedder.encode(chunks2)
    sims = util.cos_sim(e1, e2)  # [n1, n2]
    results = []
    for i in range(sims.size(0)):
        # best match j for each i
        j = int(torch.argmax(sims[i]).item())
        score = float(sims[i][j].item())
        results.append({"chunk1_idx": i, "chunk2_idx": j, "score": score})
    # take global top-k
    results = sorted(results, key=lambda x: x["score"], reverse=True)[:topk]
    return results
