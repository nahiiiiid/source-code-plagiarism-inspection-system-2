# Source Code Plagiarism Inspection System (SC-PIS)

A **production-grade**, extensible, and explainable system for detecting source-code plagiarism using **CodeBERT** embeddings, **chunk-level alignment**, **token/winnowing fingerprints**, and a **hybrid ensemble score**. Includes a polished Flask web UI, a CLI, unit tests, Dockerization, CI, and deployment notes for Hugging Face Spaces / Colab.

## Features
- 🔥 **Modern embeddings** via Sentence-Transformers (CodeBERT fine-tuned for code clones).
- 🧠 **Hybrid scoring** (ensemble of embedding similarity, token Jaccard, and winnowing fingerprint overlap).
- 🧩 **Chunking & alignment**: function-aware or sliding-window chunking, then top-k cross-chunk matching.
- 🔍 **Explainability**: suspicious regions highlighted with diff overlays and per-chunk similarity heatmaps.
- 🧪 **Tests**: pytest-based smoke and scoring tests with fixtures.
- 🐳 **Docker**: build and run with one command.
- 🚀 **CLI**: compare two files headlessly, JSON output.
- 🧰 **Production niceties**: config, logging, error handling, input validation, file size/type checks.
- 🧾 **OpenAPI**: documented REST endpoints (`/api/compare`).

## Quickstart
```bash
# 1) Python env
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip

# 2) Install deps
pip install -r requirements.txt

# 3) Run server
export FLASK_APP=app.web:create_app
flask run  # http://127.0.0.1:5000/

# or python -m app.web
python -m app.web

# 4) CLI usage
python -m app.cli compare sample_data/py/a.py sample_data/py/b.py --json out.json

or

python -m flask --app app.web:create_app run


# 5) Tests
pytest -q
```

> First run will download the embedding model from Hugging Face. Internet is required at least once.

## API (OpenAPI summary)
- `POST /api/compare` (multipart/form-data) with `file1`, `file2`, optional `language`.
- Response: JSON with ensemble score, component scores, chunk matches, and diff spans.

## Deployment
- **Docker**: `docker build -t scpis . && docker run -p 5000:5000 scpis`
- **Hugging Face Spaces**: set Space type to Gradio or Static + start `python -m app.web`
- **Colab**: open `notebooks/SC-PIS_Colab.ipynb` (optional; create later)

## License
MIT
