import argparse, json, sys
from engine.scorer import HybridScorer
from engine.explain import highlight_similar_regions
from config import Config


def compare_files(path1: str, path2: str, out_json: str = None):
    with open(path1, 'r', encoding='utf-8', errors='ignore') as f:
        code1 = f.read()
    with open(path2, 'r', encoding='utf-8', errors='ignore') as f:
        code2 = f.read()
    scorer = HybridScorer(Config.MODEL_NAME, device=Config.DEVICE, topk_matches=Config.TOPK_CHUNK_MATCHES)
    report = scorer.score(code1, code2)
    spans = highlight_similar_regions(code1, code2)
    result = {
        "threshold": Config.SIM_THRESHOLD,
        "ensemble_score": report['ensemble_score'],
        "components": report['components'],
        "chunk_matches": report['chunks']['topk_matches'],
        "spans": spans['spans']
    }
    if out_json:
        with open(out_json, 'w') as f:
            json.dump(result, f, indent=2)
    else:
        print(json.dumps(result, indent=2))

def main():
    p = argparse.ArgumentParser(prog="scpis", description="Source Code Plagiarism Inspection System CLI")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compare", help="Compare two code files") 
    c.add_argument("file1")
    c.add_argument("file2")
    c.add_argument("--json", dest="out_json", default=None, help="Write JSON report to file")
    args = p.parse_args()
    if args.cmd == "compare":
        compare_files(args.file1, args.file2, args.out_json)

if __name__ == '__main__':
    main()
