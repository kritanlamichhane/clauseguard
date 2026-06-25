# ClauseGuard 🛡️
> Know what you're signing.

ClauseGuard is an AI-powered contract risk analyzer for small businesses and freelancers. Upload any contract (PDF or Word), and get a plain-English risk report with flagged clauses and an overall risk score — in seconds.

---

## The Problem
Small businesses sign contracts all the time but can't afford a lawyer to review every one. They either sign blindly or waste money on legal fees for routine documents.

## The Solution
ClauseGuard runs every clause through a multi-stage NLP pipeline — combining rule-based pattern matching, a trained ML classifier, semantic similarity search, and LLM reasoning — to flag risky clauses and explain them in plain English.

---

## Features
- Upload PDF or Word contracts (or paste raw text)
- Named Entity Recognition — auto-extracts parties, dates, and amounts
- Rule-based risk flagging using legal-pattern regex
- ML-based clause type classification (Logistic Regression + TF-IDF)
- Semantic similarity matching against known risky clause patterns (sentence embeddings)
- LLM-powered final risk analysis and plain-English explanations (Gemini)
- Overall weighted risk score (0–100) with breakdown by severity
- Clean web interface — upload page + annotated risk report

---

## NLP Pipeline

```
contract file (PDF/DOCX)
        ↓
extractor.py     → raw text extraction
        ↓
cleaner.py       → text normalization, noise removal
        ↓
segmenter.py     → clause boundary detection (spaCy sentence segmentation + numbered-clause regex)
        ↓
ner.py           → named entity recognition: parties, dates, amounts, locations (spaCy)
        ↓
keywords.py      → keyword extraction (TF-IDF + YAKE)
        ↓
rules.py         → rule-based risk flagging (regex pattern library)
        ↓
classifier.py    → ML clause-type classification (TF-IDF + Logistic Regression, trained on 93 labeled examples / 11 categories)
        ↓
similarity.py    → semantic similarity search against known risky clauses (sentence-transformers embeddings + cosine similarity)
        ↓
analyzer.py      → final risk judgment + plain-English explanation (Gemini API, fed structured context from all prior steps)
        ↓
scorer.py        → weighted risk scoring algorithm (0–100) + severity breakdown
        ↓
risk report
```

### NLP / ML concepts demonstrated
| Concept | File | Technique |
|---|---|---|
| Text preprocessing | `cleaner.py` | regex-based normalization |
| Sentence/clause segmentation | `segmenter.py` | spaCy statistical sentence boundary detection |
| Named Entity Recognition | `ner.py` | spaCy pretrained NER model |
| Keyword extraction | `keywords.py` | TF-IDF, YAKE |
| Rule-based classification | `rules.py` | regex pattern matching |
| Supervised ML classification | `classifier.py` | TF-IDF vectorization + Logistic Regression |
| Semantic similarity / embeddings | `similarity.py` | sentence-transformers (`all-MiniLM-L6-v2`), cosine similarity |
| LLM-augmented reasoning | `analyzer.py` | prompt engineering with structured context injection |
| Applied scoring logic | `scorer.py` | weighted aggregation |

---

## Tech Stack
| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Classic NLP | spaCy, scikit-learn, YAKE |
| ML | scikit-learn (Logistic Regression) |
| Embeddings | sentence-transformers |
| LLM | Google Gemini API |
| File Parsing | pdfplumber, python-docx |
| Frontend | HTML, CSS, JavaScript |
| Environment | Conda (Python 3.11) |

---

## Project Structure
```
clauseguard/
│
├── backend/
│   ├── main.py              # FastAPI server — /analyze endpoint
│   ├── extractor.py         # PDF/DOCX → raw text
│   ├── cleaner.py           # text normalization
│   ├── segmenter.py         # clause boundary detection
│   ├── ner.py                # named entity recognition
│   ├── keywords.py          # TF-IDF + YAKE keyword extraction
│   ├── rules.py             # regex-based risk flagging
│   ├── classifier.py        # ML clause-type classifier
│   ├── similarity.py        # semantic similarity matching
│   ├── analyzer.py          # Gemini-powered final analysis
│   ├── scorer.py            # risk score calculation
│   └── models.py            # Pydantic data models
│
├── frontend/
│   ├── index.html           # upload page
│   └── report.html          # risk report page
│
├── data/
│   └── training_data/
│       ├── clauses.csv               # labeled training data (93 examples, 11 categories)
│       ├── clause_classifier.joblib  # trained model
│       └── tfidf_vectorizer.joblib   # fitted vectorizer
│
├── uploads/                 # temp storage, files deleted after processing
├── tests/                   # test scripts for each pipeline stage
│
├── .env                     # API keys (not committed)
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

### 2. Create and activate environment
```bash
conda create -n clauseguard python=3.11 -y
conda activate clauseguard
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Add your API key
Create a `.env` file in the root folder:
```
GEMINI_API_KEY=your_key_here
```

### 5. Run the backend
```bash
uvicorn backend.main:app --reload
```
API docs available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 6. Open the frontend
Open `frontend/index.html` directly in your browser (or use a Live Server extension), then upload a contract.

---

## Known Limitations
- The ML classifier is trained on a small demonstration dataset (93 examples across 11 categories). Production use would require hundreds of labeled examples per category for reliable accuracy.
- Risk pattern library (`rules.py`) and reference clauses (`similarity.py`) cover common contract risks but are not exhaustive or a substitute for legal review.
- This tool provides informational analysis only and does not constitute legal advice.

---

## Status
🚧 In active development — core pipeline and web interface functional.

---

## License
MIT