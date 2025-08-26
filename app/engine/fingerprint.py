from typing import List, Tuple, Set

def kgrams(tokens: List[str], k: int) -> List[Tuple[int, Tuple[str, ...]]]:
    out = []
    for i in range(len(tokens)-k+1):
        out.append((i, tuple(tokens[i:i+k])))
    return out

def winnowing_fingerprints(tokens: List[str], k: int = 5, window: int = 4) -> Set[Tuple[int, int]]:
    # returns set of (hash, pos) minima
    if k <= 0 or window <= 0 or len(tokens) < k:
        return set()
    kgs = kgrams(tokens, k)
    hashes = [hash(kg) for _, kg in kgs]
    res = set()
    last_min = None
    for i in range(len(hashes)-window+1):
        window_hashes = hashes[i:i+window]
        m = min(window_hashes)
        pos = i + window_hashes.index(m)
        cand = (m, pos)
        if cand != last_min:
            res.add(cand)
            last_min = cand
    return res

def fingerprint_overlap(fp1: Set[Tuple[int,int]], fp2: Set[Tuple[int,int]]) -> float:
    if not fp1 and not fp2:
        return 0.0
    inter = len(fp1 & fp2)
    union = len(fp1 | fp2) if (fp1 or fp2) else 1
    return inter / union
