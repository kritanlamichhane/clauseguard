# ClauseGuard 🛡️
> Know what you're signing.

ClauseGuard is an AI-powered contract risk analyzer for small businesses and freelancers. Upload any contract (PDF or Word), and get a plain-English risk report with flagged clauses and an overall risk score — in seconds.

---

## The Problem
Small businesses sign contracts all the time but can't afford a lawyer to review every one. They either sign blindly or waste money on legal fees for routine documents.

## The Solution
ClauseGuard reads your contract, detects risky clauses (auto-renewal traps, one-sided liability, vague payment terms, IP grabs), and explains each risk in plain English.

---

## Features
- Upload PDF or Word contracts
- AI-powered clause extraction and risk detection
- Plain-English explanations for every flagged clause
- Overall risk score (0–100)
- Export risk report as PDF

---

## Tech Stack
| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| AI / NLP | Google Gemini API |
| File Parsing | pdfplumber, python-docx |
| Frontend | HTML, CSS, JavaScript |
| Environment | Conda (Python 3.11) |

---

## Project Structure
```
clauseguard/
│
├── backend/
│   ├── main.py              # FastAPI server
│   ├── extractor.py         # PDF/DOCX → raw text
│   ├── cleaner.py           # raw text → clean clauses
│   ├── analyzer.py          # clauses → Gemini API → risk report
│   └── models.py            # data structures
│
├── frontend/
│   ├── index.html           # upload page
│   └── report.html          # risk report page
│
├── uploads/                 # temp storage for uploaded contracts
├── tests/
│   └── sample_contract.pdf  # test contract
│
├── .env                     # API keys (never commit this)
├── requirements.txt         # project dependencies
└── README.md                # you are here
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
```

### 4. Add your API key
Create a `.env` file in the root folder:
```
GEMINI_API_KEY=your_key_here
```

### 5. Run the server
```bash
uvicorn backend.main:app --reload
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

---

## Status
🚧 Currently in development.

---

## License
MIT