# AI Legal Assistant for Government

A full-stack, AI-powered legal case management system for government agencies, law enforcement, legal departments, and public grievance cells.

## Features

- **14 functional modules** — case creation, AI classification, dynamic questionnaire, evidence checklist, law identification, explainability, claim strength scoring, gap analysis, recommended actions, timeline, document generation, dashboard, case history, settings
- **7 legal domains** — Criminal, Property, Family, Consumer, Labor, Cyber, Administrative
- **Dual AI engine** — OpenAI GPT-4o-mini (if key provided) + built-in rule-based fallback
- **Document generation** — PDF and DOCX (Complaint Draft, FIR Draft, Legal Notice, Case Summary, Investigation Report)
- **Dark / Light mode**
- **Fully functional without an OpenAI key** (rule-based engine handles all analysis)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite, React Router, Axios, Recharts, react-hot-toast |
| Backend | Python 3.10+, FastAPI, SQLAlchemy, Pydantic |
| Database | SQLite (dev) → PostgreSQL (prod) |
| AI | OpenAI GPT-4o-mini + Hybrid Rule Engine |
| Documents | reportlab (PDF), python-docx (DOCX) |
| Deployment | Vercel (frontend) + Render (backend) |

---

## Project Structure

```
legal-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings from .env
│   │   ├── database/            # SQLAlchemy engine and session
│   │   ├── models/              # SQLAlchemy ORM models (12 tables)
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── routes/              # API routers (cases, analysis, questionnaire, documents, settings)
│   │   ├── services/            # Business logic (case_service, ai_service, document_service)
│   │   └── utils/               # Knowledge base loader
│   ├── knowledge_base/          # JSON legal data for 7 domains
│   ├── app.py                   # uvicorn runner
│   ├── seed_data.py             # Demo data seeder
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/               # Dashboard, CasesList, NewCase, CaseDetail, Settings
│   │   ├── components/          # Layout (Sidebar, Header, AppLayout) + Common UI
│   │   ├── services/            # api.js — all API calls
│   │   ├── context/             # ThemeContext
│   │   └── styles/              # globals.css with CSS variables
│   └── vite.config.js
├── sample_cases/
│   └── sample_cases.json        # 7 realistic demo cases
└── README.md
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm 9+

### 1. Clone and set up backend

```bash
cd legal-assistant/backend

# Create and activate a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env if you have an OpenAI key (optional — works without it)
# OPENAI_API_KEY=sk-...

# Run the backend
python app.py
```

Backend runs at: **http://localhost:8000**
API docs at: **http://localhost:8000/api/docs**

### 2. Seed sample data (optional)

```bash
# From the backend directory
python seed_data.py
```

This creates 7 fully-analysed demo cases (one per legal domain).

### 3. Set up and run frontend

```bash
cd legal-assistant/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## API Reference

All endpoints are prefixed with `/api/v1`.

### Cases
| Method | Endpoint | Description |
|---|---|---|
| GET | `/cases` | List all cases (supports `?search=`) |
| POST | `/cases` | Create new case |
| GET | `/cases/{id}` | Get case with all related data |
| PATCH | `/cases/{id}` | Update case |
| DELETE | `/cases/{id}` | Delete case |
| POST | `/cases/{id}/documents` | Upload file to case |

### Analysis
| Method | Endpoint | Description |
|---|---|---|
| POST | `/analysis/{id}/classify` | AI classification |
| POST | `/analysis/{id}/laws` | Identify applicable laws |
| POST | `/analysis/{id}/evidence` | Recommend evidence |
| PATCH | `/analysis/{id}/evidence/{ev_id}` | Update evidence status |
| POST | `/analysis/{id}/scores` | Compute claim strength scores |
| POST | `/analysis/{id}/recommendations` | Generate recommended actions |
| POST | `/analysis/{id}/gaps` | Gap analysis |
| POST | `/analysis/{id}/timeline` | Generate timeline |
| POST | `/analysis/{id}/full-analysis` | Run all analysis steps |

### Questionnaire
| Method | Endpoint | Description |
|---|---|---|
| GET | `/questionnaire/{id}/questions` | Get category-specific questions |
| POST | `/questionnaire/{id}/responses` | Submit responses |
| GET | `/questionnaire/{id}/responses` | Get all responses |

### Documents
| Method | Endpoint | Description |
|---|---|---|
| POST | `/documents/generate` | Generate PDF or DOCX |
| GET | `/documents/case/{id}` | List generated documents |
| GET | `/documents/download/{doc_id}` | Download document |

---

## Deployment

### Frontend (Vercel)

```bash
cd frontend
npm run build
# Deploy the dist/ folder to Vercel
```

Set environment variable in Vercel:
```
VITE_API_URL=https://your-backend.render.com
```

Also update `vite.config.js` proxy to use this URL for production.

### Backend (Render)

1. Push backend to a Git repository
2. Create a new Web Service on Render
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `OPENAI_API_KEY` (optional)
   - `DATABASE_URL` (use PostgreSQL URL from Render for production)
   - `ENVIRONMENT=production`

### Migrating to PostgreSQL

Change `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

Remove `connect_args={"check_same_thread": False}` in `database.py` — it is already guarded by the sqlite check.

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | `""` | OpenAI key — leave blank for rule-based mode |
| `DATABASE_URL` | `sqlite:///./legal_assistant.db` | Database connection string |
| `UPLOAD_DIR` | `uploads` | Directory for uploaded files |
| `MAX_FILE_SIZE_MB` | `10` | Maximum upload size |
| `ENVIRONMENT` | `development` | `development` or `production` |

---

## Legal Disclaimer

This system is designed as a decision-support tool for trained legal professionals and government officials. It provides recommendations and information — not definitive legal advice. All outputs should be reviewed by a qualified legal professional before any official action is taken.

---

## License

MIT
