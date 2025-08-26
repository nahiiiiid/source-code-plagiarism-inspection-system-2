from app.engine.scorer import HybridScorer

def test_scoring_smoke():
    code_a = """
def add(a, b):
    return a + b
"""
    code_b = """
def sum_vals(x, y):
    return x + y
"""
    s = HybridScorer("mchochlov/codebert-base-cd-ft")
    report = s.score(code_a, code_b)
    assert 0.0 <= report['ensemble_score'] <= 1.0
    assert set(report['components'].keys()) == {"embedding_cos","tfidf_cos","fp_overlap"}
