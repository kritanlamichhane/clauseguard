# ClauseGuard 
> Know what you're signing.

ClauseGuard is an AI-powered contract risk analyzer and document vault for small businesses, freelancers, and legal teams. Upload any contract (PDF, DOCX, or TXT), and get a plain-English risk report with flagged clauses, ML-predicted clause types, named entity recognition, and an overall risk score — in seconds.

---

## The Problem
Small businesses sign contracts all the time but can't afford a lawyer to review every one. They either sign blindly or waste money on legal fees for routine documents.

## The Solution
ClauseGuard runs every clause through a multi-stage NLP pipeline — combining rule-based pattern matching, a trained ML classifier, semantic similarity search, and optional LLM reasoning — to flag risky clauses, explain them in plain English, and archive every audit permanently in a persistent personal document vault.

---

##  Features

- **Modern React Dashboard** — Dark mode glassmorphism UI with circular risk score gauge, interactive filters, entity tags, and slide-over clause inspector.
- **User Authentication & Authorization** — Sign up / Sign in with salted PBKDF2 password hashing and secure JWT session management.
- **Persistent Document History Vault** — Automatically saves every contract analysis to a local SQLite database (`data/clauseguard.db`). Log out and log back in anytime to search, filter, reopen, or delete past audits.
- **Upload PDF, DOCX, or TXT contracts** — Drag & drop upload or test with built-in sample contracts.
- **Named Entity Recognition** — Auto-extracts parties, dates, financial terms/amounts, and locations.
- **Smart Clause Segmentation** — Detects numbered sections and markdown headers (`## 1. Services`).
- **Rule-Based Risk Flagging** — Pattern library detecting critical legal liabilities and unfair obligations.
- **ML Clause-Type Classification** — Logistic Regression + TF-IDF classifier across 11 standard contract clause categories.
- **ONNX-Optimized Semantic Similarity Search** — Sentence embedding matching (`all-MiniLM-L6-v2`) against known predatory clause patterns.
- **LLM-Powered Contract Reasoning** — Google Gemini API with intelligent local NLP fallbacks.
- **Overall Weighted Risk Score (0–100)** — Comprehensive severity score and breakdown by risk levels (High, Medium, Low, Safe).

---

##  Architecture & NLP Pipeline

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
rules.py         → rule-based risk flagging (regex pattern library)
        ↓
classifier.py    → ML clause-type classification (TF-IDF + Logistic Regression, 11 categories)
        ↓
similarity.py    → semantic similarity search against known risky clauses (ONNX all-MiniLM-L6-v2 + cosine similarity)
        ↓
analyzer.py      → batch risk analysis: Gemini API (with NLP fallback on quota exceeded)
        ↓
scorer.py        → weighted risk scoring algorithm (0–100) + severity breakdown
        ↓
database.py      → SQLite persistent storage (data/clauseguard.db) for authenticated users
        ↓
React Dashboard  (Vite + TypeScript + Tailwind CSS UI)
```

---

##  Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, Lucide Icons, TypeScript |
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Database & Auth | SQLite (`data/clauseguard.db`), JWT (HMAC-SHA256), PBKDF2-HMAC-SHA256 |
| Classic NLP | spaCy (`en_core_web_sm`), scikit-learn, YAKE |
| ML / Embeddings | scikit-learn (Logistic Regression), **optimum (ONNX Runtime)** |
| LLM | Google Gemini API (`google-genai` SDK) |
| File Parsing | pdfplumber, python-docx |
| Package Manager | `uv` (Python) / `npm` (Frontend) |

---

##  Quick Start

### 1. Backend Setup (Python)

```bash
# Create virtual environment using uv (or standard venv)
uv venv

# Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

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

### 3. Environment Variables

Create a `.env` file in the root folder:

```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_jwt_secret_key_here
```

*(Note: If no Gemini API key is configured, ClauseGuard automatically uses local rule-based and ML analysis fallbacks.)*

### 4. Run Development Server (Both Backend & Frontend)

From the project root directory:

```bash
npm run dev
```

Open **`http://localhost:3000`** in your browser.

---

##  API Endpoints

### Authentication
- `POST /auth/register` — Create a new user account & receive a JWT access token.
- `POST /auth/login` — Sign in with email and password & receive a JWT access token.
- `GET /auth/me` — Retrieve profile details for the authenticated user.

### Document Audit & History
- `POST /analyze` — Upload and analyze a PDF/DOCX/TXT contract. If `Authorization: Bearer <token>` is present, automatically archives the audit in user history.
- `GET /history` — List all past contract audits for the authenticated user.
- `GET /history/{id}` — Fetch the complete audit report for a specific past document.
- `DELETE /history/{id}` — Delete a saved contract audit from history.
- `GET /health` — Health check endpoint for service monitoring.

---

##  Project Structure

```
clauseguard/
│
├── backend/
│   ├── main.py              # FastAPI server — routes, auth, history & static serving
│   ├── database.py          # SQLite database schema & CRUD helpers (users, history)
│   ├── auth.py              # Password hashing & JWT token verification
│   ├── models.py            # Pydantic data schemas for auth, history & reports
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
│   │   ├── components/
│   │   │   ├── AuthModal.tsx        # Login & Registration modal
│   │   │   ├── HistoryView.tsx      # Document audit vault & search/filter
│   │   │   ├── Header.tsx           # Navigation, auth profile & status
│   │   │   ├── FileUploader.tsx     # Drag & drop contract uploader
│   │   │   ├── RiskScoreCard.tsx    # Risk score gauge & AI executive summary
│   │   │   ├── RiskBreakdownBar.tsx # Interactive risk breakdown selector
│   │   │   ├── EntityPills.tsx      # Extracted parties, dates & amounts
│   │   │   ├── ClauseFilter.tsx     # Clause search and severity tabs
│   │   │   ├── ClauseCard.tsx       # Interactive clause summary card
│   │   │   └── ClauseDetailDrawer.tsx # Deep inspection drawer
│   │   ├── App.tsx          # Main application & routing state
│   │   ├── index.css        # Tailwind design system & animations
│   │   └── types.ts         # TypeScript API interfaces
│   ├── package.json
│   └── vite.config.ts       # Vite configuration with API proxies
│
├── data/
│   ├── clauseguard.db       # Persistent SQLite database (auto-created)
│   └── training_data/       # Labeled clause classification training dataset
│
├── tests/                   # Pytest test suite (21 unit & integration tests)
│   ├── test_auth_history.py # User auth, JWT, isolation & persistence tests
│   ├── test_api.py          # API endpoint tests
│   └── ...                  # Pipeline component tests
│
├── package.json             # Root package script for concurrent dev runner
├── requirements.txt         # Python dependencies
└── README.md
```

---

##  Running Tests

Run the full automated test suite:

```bash
pytest tests/
```

---

##  Limitations & Legal Disclaimer

> [!IMPORTANT]
> **Legal Disclaimer:** ClauseGuard is an automated contract auditing assistant created for informational purposes only. It does **not** constitute formal legal advice or substitute for professional legal counsel.

* **Scanned Image PDFs:** ClauseGuard currently parses native text PDFs, DOCX, and TXT files. Image-only/scanned PDFs require pre-processing with an external OCR tool.
* **Offline Model Fallback:** When offline or without a Gemini API key, executive summaries fall back to local rule-based heuristic summaries.

---

##  Future Work

- [x] **Saved Audit History & User Authentication:** Multi-user accounts with permanent contract audit archiving.
- [ ] **Fine-tuned Legal Model:** Fine-tuning transformer models directly on the CUAD (Contract Understanding Atticus Dataset) for specialized legal entity and risk detection.
- [ ] **Contract Version Comparison:** Multi-document diffing to highlight structural and risk changes between contract revisions.
- [ ] **Export Options:** One-click export of structured risk reports to PDF and Word (`.docx`) formats.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

##  Acknowledgements

* [spaCy](https://spacy.io/) for Named Entity Recognition and NLP sentence boundary parsing.
* [Hugging Face Optimum](https://huggingface.co/docs/optimum) & [ONNX Runtime](https://onnxruntime.ai/) for high-performance local embeddings execution (`all-MiniLM-L6-v2`).
* [Google Gemini API](https://ai.google.dev/) for AI LLM contract reasoning and plain-English summaries.
* [scikit-learn](https://scikit-learn.org/) for supervised machine learning clause classification.
* [Lucide Icons](https://lucide.dev/) & [Tailwind CSS](https://tailwindcss.com/) for UI elements and design system styling.