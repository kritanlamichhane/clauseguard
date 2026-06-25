# ClauseGuard 🛡️
> Know what you're signing.

ClauseGuard is an AI-powered contract risk analyzer for small businesses and freelancers. Upload any contract (PDF, DOCX, or TXT), and get a plain-English risk report with flagged clauses and an overall risk score — in seconds.

---

## The Problem
Small businesses sign contracts all the time but can't afford a lawyer to review every one. They either sign blindly or waste money on legal fees for routine documents.

## The Solution
ClauseGuard runs every clause through a multi-stage NLP pipeline — combining rule-based pattern matching, a trained ML classifier, semantic similarity search, and optional LLM reasoning — to flag risky clauses and explain them in plain English.

---

## Features
- Upload PDF, DOCX, or TXT contracts — or paste raw text directly
- Named Entity Recognition — auto-extracts parties, dates, amounts, and locations
- Smart clause segmentation — detects numbered sections and markdown headers (`## 1. Services`)
- Rule-based risk flagging using legal-pattern regex (8 risk categories)
- ML-based clause-type classification (Logistic Regression + TF-IDF, 11 categories)
- Semantic similarity matching against known risky clause patterns (sentence embeddings)
- Optional LLM-powered final analysis via Google Gemini with graceful fallback
- Overall weighted risk score (0–100) with breakdown by severity
- Clean web interface — upload page + tabbed annotated risk report

---

## NLP Pipeline

```
contract file (PDF / DOCX / TXT)
        ↓
extractor.py     → raw text extraction (pdfplumber / python-docx)
        ↓
cleaner.py       → smart line joining, noise removal, quote normalization
        ↓
segmenter.py     → clause boundary detection (markdown headers + numbered-clause regex, spaCy fallback)
        ↓
ner.py           → named entity recognition: parties, dates, amounts, locations (spaCy)
        ↓
keywords.py      → keyword extraction per clause (TF-IDF + YAKE)
        ↓
rules.py         → rule-based risk flagging (8-pattern regex library)
        ↓
classifier.py    → ML clause-type classification (TF-IDF + Logistic Regression, 93 labeled examples / 11 categories)
        ↓
similarity.py    → semantic similarity search against known risky clauses (all-MiniLM-L6-v2 + cosine similarity)
        ↓
analyzer.py      → batch risk analysis: Gemini API (with NLP fallback on quota exceeded)
        ↓
scorer.py        → weighted risk scoring algorithm (0–100) + severity breakdown
        ↓
risk report (report.html)
```

### NLP / ML Techniques Demonstrated

| Concept | File | Technique |
|---|---|---|
| Text preprocessing | `cleaner.py` | Regex normalization, smart line joining |
| Clause segmentation | `segmenter.py` | Markdown header regex, numbered-clause detection, spaCy sentence boundary fallback |
| Named Entity Recognition | `ner.py` | spaCy `en_core_web_sm` pretrained NER |
| Keyword extraction | `keywords.py` | TF-IDF (multi-doc), YAKE (single-doc) |
| Rule-based classification | `rules.py` | Regex pattern matching (8 risk types) |
| Supervised ML classification | `classifier.py` | TF-IDF vectorization + Logistic Regression |
| Semantic similarity / embeddings | `similarity.py` | `sentence-transformers` (`all-MiniLM-L6-v2`), cosine similarity |
| LLM-augmented reasoning | `analyzer.py` | Batch prompt engineering with structured context injection + Pydantic schema |
| Risk scoring logic | `scorer.py` | Weighted aggregation by severity |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, Uvicorn |
| Classic NLP | spaCy (`en_core_web_sm`), scikit-learn, YAKE |
| ML / Embeddings | scikit-learn (Logistic Regression), sentence-transformers |
| LLM | Google Gemini API (`google-genai` SDK) |
| File Parsing | pdfplumber, python-docx |
| Frontend | Vanilla HTML, CSS, JavaScript (no framework) |
| Environment | Conda (Python 3.11) |

---

## Project Structure

```
clauseguard/
│
├── backend/
│   ├── main.py              # FastAPI server — serves API + frontend static files
│   ├── extractor.py         # PDF/DOCX/TXT → raw text
│   ├── cleaner.py           # Smart text normalization (structure-aware line joining)
│   ├── segmenter.py         # Clause boundary detection (markdown + numbered regex)
│   ├── ner.py               # Named entity recognition (spaCy)
│   ├── keywords.py          # TF-IDF + YAKE keyword extraction
│   ├── rules.py             # Regex-based risk flagging (8 patterns)
│   ├── classifier.py        # ML clause-type classifier (train + predict)
│   ├── similarity.py        # Semantic similarity matching (sentence-transformers)
│   ├── analyzer.py          # Gemini batch analysis + NLP fallback
│   ├── scorer.py            # Risk score calculation (0–100)
│   └── models.py            # Pydantic data models
│
├── frontend/
│   ├── index.html           # Contract upload page
│   ├── report.html          # Tabbed risk report page
│   └── assets/
│       ├── style.css        # Shared stylesheet
│       ├── script.js        # Upload logic + API call
│       └── report.js        # Report rendering (gauge, tabs, clauses)
│
├── data/
│   └── training_data/
│       ├── clauses.csv               # Labeled training data (93 examples, 11 categories)
│       ├── clause_classifier.joblib  # Trained model (auto-generated)
│       └── tfidf_vectorizer.joblib   # Fitted vectorizer (auto-generated)
│
├── tests/
│   ├── sample_contract.pdf  # Sample PDF for testing
│   ├── test_extractor.py    # PDF/TXT extraction tests
│   ├── test_cleaner.py      # Text normalization tests
│   ├── test_segmenter.py    # Clause segmentation tests
│   ├── test_rules.py        # Rule-based flagging tests
│   ├── test_classifier.py   # ML classifier train + predict test
│   ├── test_keywords.py     # TF-IDF + YAKE keyword tests
│   ├── test_ner.py          # Named entity recognition tests
│   ├── test_similarity.py   # Semantic similarity tests
│   └── test_analyzer        # End-to-end batch analysis test
│
├── uploads/                 # Temporary file storage (auto-cleared after processing)
├── .env                     # API keys (never commit this)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/clauseguard.git
cd clauseguard
```

### 2. Create and activate the Conda environment

```bash
conda create -n clauseguard python=3.11 -y
conda activate clauseguard
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Add your Gemini API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Get a free key at [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).

> **Note:** If you hit the free-tier quota limit (20 req/day), ClauseGuard automatically falls back to local NLP heuristics — the app still works, just without Gemini explanations.

### 5. Run the server

**The backend also serves the frontend — you only need one command:**

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Wait ~15–30 seconds for the ML models (spaCy, SentenceTransformer) to load on first startup.

### 6. Open in your browser

| URL | Purpose |
|---|---|
| `http://127.0.0.1:8000` | Main upload page |
| `http://127.0.0.1:8000/docs` | Swagger API documentation |
| `http://127.0.0.1:8000/health` | Health check endpoint |

---

## Running Tests

Run each pipeline stage independently from the project root:

```bash
# Activate environment first
conda activate clauseguard

# Individual tests
python tests/test_extractor.py
python tests/test_cleaner.py
python tests/test_segmenter.py
python tests/test_rules.py
python tests/test_ner.py
python tests/test_keywords.py
python tests/test_similarity.py
python tests/test_classifier.py

# End-to-end pipeline test (uses Gemini)
python tests/test_analyzer
```

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `uvicorn: not recognized` | Active env not set | Run with full path or `conda activate clauseguard` first |
| `Address already in use` on port 8000 | Old server still running | `netstat -ano \| findstr :8000` then `taskkill /PID <id> /F` |
| `ModuleNotFoundError` | Wrong working directory | Always run from `D:\Project\clauseguard` |
| `429 RESOURCE_EXHAUSTED` | Gemini free-tier quota hit | Fallback NLP kicks in automatically — analysis still works |
| `No model named pytest` | pytest not installed | `pip install pytest` |
| Models load slowly on first run | Downloading weights | Normal — subsequent starts are faster |

---

## Known Limitations

- The ML classifier is trained on a small demonstration dataset (93 examples across 11 categories). Production use would require hundreds of labeled examples per category for reliable accuracy.
- Risk pattern library (`rules.py`) and reference clauses (`similarity.py`) cover common contract risks but are not exhaustive.
- On the Gemini free tier, the daily quota (20 requests/day for `gemini-2.5-flash`) may be exceeded quickly during testing. The local NLP fallback handles this gracefully.
- This tool provides **informational analysis only** and does not constitute legal advice. Always consult a qualified attorney for important contracts.

---

## Status

✅ Core pipeline functional — extractor, cleaner, segmenter, NER, rules, classifier, similarity, scoring  
✅ Web interface — upload page + tabbed risk report (Flagged Clauses, NER, Classification, Summary)  
✅ Gemini batch analysis with graceful NLP fallback  
🚧 In active development

---

## License

MIT