# streamlit_app.py
# Streamlit UI for SOURCE-CODE-PLAGIARISM-INSPECTION-SYSTEM
# Reuses your existing engine (HybridScorer) and explain utilities.

import os
import sys
from typing import List, Dict, Tuple

import streamlit as st

# --- make 'app' importable when we run from repo root
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(REPO_DIR, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from config import Config
from engine.scorer import HybridScorer
from engine.explain import highlight_similar_regions


# ----- Helpers

def get_env_or_secret(name: str, default: str):
    """
    Prefer environment variable, then Streamlit secrets (if present), then default.
    """
    val = os.getenv(name, None)
    if val is not None:
        return val
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


def allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = "." + filename.rsplit(".", 1)[1].lower()
    return ext in Config.ALLOWED_EXTENSIONS


@st.cache_resource(show_spinner=True)
def load_scorer() -> HybridScorer:
    model_name = get_env_or_secret("MODEL_NAME", Config.MODEL_NAME)
    device = get_env_or_secret("DEVICE", Config.DEVICE)
    topk = int(get_env_or_secret("TOPK_CHUNK_MATCHES", str(Config.TOPK_CHUNK_MATCHES)))
    return HybridScorer(model_name, device=device, topk_matches=topk)


def to_percent(x: float) -> float:
    try:
        return round(float(x) * 100.0, 2)
    except Exception:
        return 0.0


def _build_marks(code: str, ranges: List[Tuple[int, int]]) -> str:
    """
    Return HTML with <mark> around the provided character index ranges.
    Assumes ranges are non-overlapping or will be merged below.
    """
    if not ranges:
        # Escape and wrap in <pre>
        import html
        return f"<pre>{html.escape(code)}</pre>"

    # Merge/normalize ranges
    ranges = sorted([(max(0, s), max(0, e)) for s, e in ranges if e > s], key=lambda x: x[0])
    merged = []
    for s, e in ranges:
        if not merged or s > merged[-1][1]:
            merged.append([s, e])
        else:
            merged[-1][1] = max(merged[-1][1], e)

    # Build HTML with marks
    out = []
    last = 0
    import html
    for s, e in merged:
        if last < s:
            out.append(html.escape(code[last:s]))
        out.append(f"<mark>{html.escape(code[s:e])}</mark>")
        last = e
    if last < len(code):
        out.append(html.escape(code[last:]))

    return "<pre>" + "".join(out) + "</pre>"


def render_highlights(code1: str, code2: str, spans_obj: Dict) -> Tuple[str, str]:
    """
    Convert spans from highlight_similar_regions() into HTML for both sides.
    We accept either:
      - {'spans': [{'a': [s,e], 'b': [s,e]}, ...]}
      - or {'spans1': [[s,e],...], 'spans2': [[s,e],...]}
    """
    spans = spans_obj or {}
    spans_list = spans.get("spans", [])
    spans1 = spans.get("spans1")
    spans2 = spans.get("spans2")

    a_ranges, b_ranges = [], []

    if spans1 is not None or spans2 is not None:
        # Explicit ranges per side
        a_ranges = [(int(s), int(e)) for s, e in (spans1 or [])]
        b_ranges = [(int(s), int(e)) for s, e in (spans2 or [])]
    else:
        # Pairs with 'a' and 'b'
        for item in spans_list:
            a = item.get("a")
            b = item.get("b")
            if a and len(a) == 2:
                a_ranges.append((int(a[0]), int(a[1])))
            if b and len(b) == 2:
                b_ranges.append((int(b[0]), int(b[1])))

    html1 = _build_marks(code1, a_ranges)
    html2 = _build_marks(code2, b_ranges)
    return html1, html2


# ----- UI

st.set_page_config(page_title="Source Code Plagiarism Inspection", layout="wide")

st.title("🔍 Source Code Plagiarism Inspection System")
st.caption("Streamlit front-end (CodeBERT hybrid similarity).")

with st.expander("⚙️ Settings (optional)"):
    st.write("These default to your `Config` / environment. You can override here for this session.")
    model_name_ui = st.text_input("Model name", value=get_env_or_secret("MODEL_NAME", Config.MODEL_NAME))
    device_ui = st.selectbox("Device", options=["cpu", "cuda"], index=0 if get_env_or_secret("DEVICE", Config.DEVICE) == "cpu" else 1)
    sim_threshold_ui = st.slider("Suspicion threshold (%)", min_value=50, max_value=99, value=int(float(get_env_or_secret("SIM_THRESHOLD", str(Config.SIM_THRESHOLD))) * 100), step=1)
    topk_ui = st.number_input("Top-K chunk matches", min_value=1, max_value=20, value=int(get_env_or_secret("TOPK_CHUNK_MATCHES", str(Config.TOPK_CHUNK_MATCHES))), step=1)
    # These UI overrides don’t rebuild the cached scorer. If you need to force reload with a different model/device,
    # rerun with env vars set, or toggle "Clear cache" from Streamlit menu.

st.divider()

colL, colR = st.columns(2)

with colL:
    f1 = st.file_uploader("Upload File A", type=[e.strip(".") for e in Config.ALLOWED_EXTENSIONS], key="file1")
with colR:
    f2 = st.file_uploader("Upload File B", type=[e.strip(".") for e in Config.ALLOWED_EXTENSIONS], key="file2")

compare_btn = st.button("Compare", type="primary", disabled=not (f1 and f2))

if compare_btn:
    if not (f1 and f2):
        st.error("Please upload both files.")
        st.stop()

    if not (allowed_file(f1.name) and allowed_file(f2.name)):
        st.error("Unsupported file type.")
        st.stop()

    code1 = f1.read().decode("utf-8", errors="ignore")
    code2 = f2.read().decode("utf-8", errors="ignore")

    with st.spinner("Loading model and computing scores..."):
        scorer = load_scorer()
        report = scorer.score(code1, code2)
        spans = highlight_similar_regions(code1, code2)

    ensemble = float(report.get("ensemble_score", 0.0))
    components = report.get("components", {})
    chunk_matches = report.get("chunks", {}).get("topk_matches", [])
    suspicious = ensemble >= (sim_threshold_ui / 100.0)

    # --- Summary header
    st.subheader("Result")
    st.metric(
        label="Ensemble similarity",
        value=f"{to_percent(ensemble)}%",
        delta="Suspicious" if suspicious else "Not suspicious",
        delta_color="inverse" if suspicious else "normal"
    )
    st.caption(f"Threshold: {sim_threshold_ui}%")

    # --- Component scores
    if components:
        st.write("**Component scores**")
        st.table({k: [f"{to_percent(v)}%"] for k, v in components.items()})

    # --- Top-K chunk matches
    if chunk_matches:
        st.write("**Top-K chunk matches**")
        # Normalize to a readable table
        rows = []
        for m in chunk_matches:
            rows.append({
                "score %": to_percent(m.get("score", 0.0)),
                "A start": m.get("a_start"),
                "A end": m.get("a_end"),
                "B start": m.get("b_start"),
                "B end": m.get("b_end"),
            })
        st.dataframe(rows, use_container_width=True)

    # --- Highlighted code
    st.subheader("Highlighted overlaps")
    html1, html2 = render_highlights(code1, code2, spans)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**File A**")
        st.components.v1.html(
            f"""
            <style>
              pre {{ white-space: pre-wrap; word-wrap: break-word; }}
              mark {{ background-color: #ffff00; }}
            </style>
            {html1}
            """,
            height=450,
            scrolling=True,
        )
    with c2:
        st.markdown("**File B**")
        st.components.v1.html(
            f"""
            <style>
              pre {{ white-space: pre-wrap; word-wrap: break-word; }}
              mark {{ background-color: #aff8db; }}
            </style>
            {html2}
            """,
            height=450,
            scrolling=True,
        )

    st.success("Done.")
else:
    st.info("Upload two code files and click **Compare**.")