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
- **Modern React Dashboard** — Dark mode glassmorphism UI with circular risk score gauge, interactive filters, entity tags, and slide-over inspector.
- **Upload PDF, DOCX, or TXT contracts** — Drag & drop upload or test with built-in sample contract.
- **Named Entity Recognition** — Auto-extracts parties, dates, amounts, and locations.
- **Smart clause segmentation** — Detects numbered sections and markdown headers (`## 1. Services`).
- **Rule-based risk flagging** using legal-pattern regex (8 risk categories).
- **ML-based clause-type classification** (Logistic Regression + TF-IDF, 11 categories).
- **ONNX-optimized Semantic similarity matching** against known risky clause patterns (fast local embedding execution).
- **LLM-powered final analysis** via Google Gemini with graceful fallback.
- **Overall weighted risk score (0–100)** with breakdown by severity.

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
similarity.py    → semantic similarity search against known risky clauses (ONNX all-MiniLM-L6-v2 + cosine similarity)
        ↓
analyzer.py      → batch risk analysis: Gemini API (with NLP fallback on quota exceeded)
        ↓
scorer.py        → weighted risk scoring algorithm (0–100) + severity breakdown
        ↓
React Dashboard (Vite + Tailwind CSS UI)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, Lucide Icons, TypeScript |
| Backend | Python 3.11, FastAPI, Uvicorn |
| Classic NLP | spaCy (`en_core_web_sm`), scikit-learn, YAKE |
| ML / Embeddings | scikit-learn (Logistic Regression), **optimum (ONNX Runtime)** |
| LLM | Google Gemini API (`google-genai` SDK) |
| File Parsing | pdfplumber, python-docx |
| Package Manager | `uv` (Python) / `npm` (Frontend) |

---

## Quick Start

### 1. Backend Setup (Python)

```bash
# Create virtual environment using uv (or standard venv)
uv venv

# Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 2. Frontend Setup (React + Vite)

```bash
# Install root dependencies
npm install

# Install frontend dependencies
cd frontend && npm install && cd ..
```

### 3. Run Development Server (Both Backend & Frontend)

From the project root directory:

```bash
npm run dev
```

Open **`http://localhost:3000`** in your browser.

---

## Project Structure

```
clauseguard/
│
├── backend/
│   ├── main.py              # FastAPI server — serves API + frontend static files
│   ├── extractor.py         # PDF/DOCX/TXT → raw text
│   ├── cleaner.py           # Smart text normalization
│   ├── segmenter.py         # Clause boundary detection
│   ├── ner.py               # Named entity recognition (spaCy)
│   ├── keywords.py          # TF-IDF + YAKE keyword extraction
│   ├── rules.py             # Regex-based risk flagging
│   ├── classifier.py        # ML clause-type classifier
│   ├── similarity.py        # Semantic similarity search (ONNX Runtime)
│   ├── analyzer.py          # Gemini API batch risk analysis & local fallbacks
│   ├── scorer.py            # Weighted risk scoring algorithm (0–100)
│   └── constants.py         # Reference risk database & regex patterns
│
├── frontend/                # Vite + React 18 + Tailwind CSS SPA
│   ├── src/
│   │   ├── components/      # React components (RiskScoreCard, ClauseFilter, etc.)
│   │   ├── App.tsx          # Main React application
│   │   ├── index.css        # Tailwind tokens & glassmorphism CSS
│   │   └── types.ts         # TypeScript API interfaces
│   ├── package.json
│   └── vite.config.ts
│
├── package.json             # Root package script for concurrent dev runner
├── requirements.txt         # Python dependencies
└── README.md
```