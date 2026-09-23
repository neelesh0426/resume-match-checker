# Resume Match Score Checker 🎯

> An intelligent, transparent, and explainable ATS resume matching engine with AI-powered semantic similarity scoring, skills taxonomy breakdown, and actionable ATS improvement tips.

---

## 🌟 Key Features

- **Multi-Format Resume Ingestion**: Supports `.pdf` (via `pdfplumber` with Tesseract OCR fallback for scanned resumes) and `.docx` (via `python-docx`).
- **Explainable 0–100 Scoring Formula**:
  - **40% Required Core Skills Match**: Direct and alias-matched essential skills.
  - **20% Semantic Relevance**: Cosine similarity between resume and job description using `all-MiniLM-L6-v2` transformer sentence embeddings.
  - **20% Preferred Skills Match**: Bonus points for nice-to-have qualifications.
  - **10% Role & Experience Alignment**: Title and seniority matching.
  - **10% Resume Completeness**: Contact details, structured sections, and education.
- **Advanced Skills Taxonomy**: spaCy `PhraseMatcher` combined with `RapidFuzz` for fuzzy alias resolution across Languages, Frameworks, Databases, Cloud/DevOps, and Soft Skills.
- **Actionable Optimization Tips**: Priority-tagged (`High`, `Medium`, `Low`) recommendations highlighting exact keywords and bullet points to add.
- **Zero Resume Retention**: Resumes are parsed in temporary storage and deleted immediately after processing for privacy.
- **Modern React + Vite Frontend**: Dark obsidian theme with glassmorphic cards, animated SVG circular progress gauge, and responsive mobile-ready layout.

---

## 🏗️ Architecture

```
resume-match-checker/
├── backend/
│   ├── app/
│   │   ├── models/            # SQLAlchemy database models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── services/          # Extractor, Scorer, Skills, Model Loader
│   │   ├── config.py          # App settings & CORS configuration
│   │   ├── database.py        # SQLite engine & session management
│   │   └── main.py            # FastAPI endpoints (/api/health, /api/analyze)
│   ├── tests/                 # Comprehensive test suite (18 unit & integration tests)
│   ├── pytest.ini             # Test runner configuration
│   └── requirements.txt       # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── components/        # Gauge, Uploader, Breakdown, SkillsMatrix, Suggestions
    │   ├── services/          # API fetch client
    │   ├── App.jsx            # Root application state & UI
    │   └── index.css          # Vanilla CSS design system
    ├── index.html             # Google Fonts & SEO meta tags
    ├── package.json           # React 19 & Lucide icons
    └── vite.config.js         # Dev server with /api proxy
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+** (Tested on Python 3.11 – 3.14)
- **Node.js 18+** and **npm**

---

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv .venv

# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy English language model
python -m spacy download en_core_web_sm

# Run automated tests
pytest -v

# Start the FastAPI development server
uvicorn app.main:app --reload --port 8000
```

The backend will be running at `http://127.0.0.1:8000`.
Interactive Swagger API documentation is available at `http://127.0.0.1:8000/docs`.

---

### 2. Frontend Setup

In a new terminal window:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

Open your browser at **`http://localhost:5173/`**.

---

## 🧪 Testing

The backend includes full unit and integration test coverage:

```bash
cd backend
pytest -v
```

Tests cover:
- Health check and API validation (`test_api.py`)
- PDF and DOCX parsing, extraction, and error handling (`test_parser.py`)
- Scoring mathematical bounds and weightings (`test_scorer.py`)
- Skills extraction, alias normalization, and fuzzy matching (`test_skills.py`)

---

## 📄 License

MIT License. Free to use for personal and commercial projects.
