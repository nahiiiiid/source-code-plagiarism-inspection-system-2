import re
from typing import List

SINGLE_LINE_COMMENTS = [
    (r"//.*?$", re.MULTILINE),          # C/C++/Java/JS
    (r"#.*?$", re.MULTILINE),           # Python
    (r"--.*?$", re.MULTILINE),          # SQL
]
MULTI_LINE_COMMENTS = [
    (r"/\*.*?\*/", re.DOTALL),       # C-style
    (r'"""[\s\S]*?"""', 0),     # Python triple double
    (r"\'\'\'[\s\S]*?\'\'\'", 0),  # Python triple single
]

def strip_comments(code: str) -> str:
    s = code
    for pat, flags in SINGLE_LINE_COMMENTS:
        s = re.sub(pat, "", s, flags=flags)
    for pat, flags in MULTI_LINE_COMMENTS:
        s = re.sub(pat, "", s, flags=flags)
    return s

def normalize_code(code: str) -> str:
    # remove comments, normalize whitespace, collapse literals
    s = strip_comments(code)
    # normalize whitespace
    s = re.sub(r"\r\n|\r", "\n", s)
    s = re.sub(r"\t", " ", s)
    s = re.sub(r" +", " ", s)
    s = re.sub(r"\n{2,}", "\n\n", s)
    # mask strings and numbers
    s = re.sub(r"\".*?\"|\'.*?\'", '"STR"', s)
    s = re.sub(r"\b\d+(?:\.\d+)?\b", 'NUM', s)
    return s.strip()

def simple_tokenize(code: str) -> List[str]:
    # split by alnum boundaries and punctuation
    toks = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\S", code)
    return toks
