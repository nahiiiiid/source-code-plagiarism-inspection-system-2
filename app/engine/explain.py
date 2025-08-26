from typing import List, Dict, Any, Tuple
from diff_match_patch import diff_match_patch

def highlight_similar_regions(a: str, b: str, threshold: float = 0.8) -> Dict[str, Any]:
    # simple char-level diff; in UI we render insert/delete/equals
    dmp = diff_match_patch()
    diffs = dmp.diff_main(a, b)
    dmp.diff_cleanupSemantic(diffs)
    # compress result: provide spans of equal segments longer than certain length
    spans = []
    pos_a, pos_b = 0, 0
    for op, data in diffs:
        length = len(data)
        if op == 0:  # equal
            if length >= 20:  # heuristic min span length
                spans.append({"a_start": pos_a, "a_end": pos_a+length, "b_start": pos_b, "b_end": pos_b+length, "text": data[:200]})
            pos_a += length
            pos_b += length
        elif op == -1:  # deletion from a
            pos_a += length
        else:  # insertion to b
            pos_b += length
    return {"spans": spans, "raw_diffs": diffs}
