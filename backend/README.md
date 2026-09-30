# ResumeMate Backend 🚀

High-performance, async REST API for **ResumeMate** built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy (asyncio)**.

---

## 🛠️ Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.14+)
- **Database:** [PostgreSQL](https://www.postgresql.org/) with async [asyncpg](https://magicstack.github.io/asyncpg/) & [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Document Parsers:** [pypdf](https://pypdf.readthedocs.io/) (PDF extraction) & [python-docx](https://python-docx.readthedocs.io/) (Word docs)
- **Security:** `bcrypt` password hashing & `PyJWT` bearer token authentication
- **Data Validation:** Pydantic v2 & `pydantic-settings`
- **AI Integration:** Google Gemini API (optional) + built-in heuristic NLP resume matching & ATS scoring engine

---

## 📁 Project Architecture

```
backend/
├── app/
│   ├── config.py              # Environment settings & configuration
│   ├── database.py            # Async engine, sessionmaker, and DB connection
│   ├── models/                # SQLAlchemy ORM models
│   │   ├── user.py            # Users & notifications
│   │   ├── resume.py          # Saved resumes & uploaded files
│   │   ├── job.py             # Target job postings
│   │   └── history.py         # Analysis audit history
│   ├── schemas/               # Pydantic v2 request/response schemas
│   │   ├── auth.py            # Login, register, profile
│   │   ├── resume.py          # Builder & parsed resume structures
│   │   ├── job.py             # Job descriptions
│   │   ├── analysis.py        # Match scoring, skill gaps, ATS checklist
│   │   └── chat.py            # Chat messages & AI suggestions
│   ├── services/              # Business logic & AI/NLP engines
│   │   ├── auth_service.py    # Password hashing & JWT verification
│   │   ├── parser_service.py  # PDF/DOCX text & entity extractor
│   │   ├── skill_extractor.py # Canonical taxonomy of 250+ tech skills
│   │   ├── matcher_service.py # Weighted match score & ATS calculator
│   │   ├── recommendations.py # Curated study roadmaps & free resources
│   │   └── ai_service.py      # Context-aware chat & Gemini LLM
│   └── routers/               # FastAPI endpoints
│       ├── auth.py            # /api/auth (register, login, me)
│       ├── users.py           # /api/users (profile, notifications)
│       ├── resumes.py         # /api/resumes (CRUD, duplicate, upload)
│       ├── jobs.py            # /api/jobs (samples, parse URL/text)
│       ├── analyze.py         # /api/analyze (full matching pipeline)
│       ├── history.py         # /api/history (audit logs)
│       ├── dashboard.py       # /api/dashboard/stats
│       └── chat.py            # /api/chat & suggestions
├── main.py                    # Application entrypoint & lifespan
├── run.py                     # Convenience runner: python run.py
├── init_db.py                 # Automated PostgreSQL DB creation & migration
├── requirements.txt           # Python package dependencies
└── .env                       # Environment configuration
```

---

## ⚡ Quick Start

### 1. Environment Setup & Dependencies

```bash
# Navigate to backend directory
cd backend

# If using uv (fastest):
uv venv .venv
.\.venv\Scripts\activate
uv pip install -r requirements.txt

# Or using standard python:
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure PostgreSQL Credentials in `.env`

Edit `backend/.env` with your PostgreSQL database credentials:

```env
DB_USER=postgres
DB_PASSWORD=your_actual_password_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=resume_analyzer_db

# Async Database URL
DATABASE_URL=postgresql+asyncpg://postgres:your_actual_password_here@localhost:5432/resume_analyzer_db

# Optional: Google Gemini API key for deep AI insights and chatbot
GEMINI_API_KEY=""
```

> **Note:** If PostgreSQL credentials are not yet set or the database is unreachable, the server automatically initializes a local SQLite database (`backend/data/resume_analyzer.db`) as a graceful development fallback, so the app remains 100% functional.

### 3. Initialize & Seed Database

Run the automated initialization script to create the PostgreSQL database and tables:

```bash
python init_db.py
```

### 4. Run the Backend Server

```bash
python run.py
```

The server starts at `http://127.0.0.1:8000`.

- **Interactive Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check:** [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## 📡 API Endpoints Overview

| Category | Method | Path | Description |
| :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/api/auth/register` | Register new candidate account |
| **Auth** | `POST` | `/api/auth/login` | Authenticate with email & password |
| **Auth** | `GET` | `/api/auth/me` | Fetch authenticated user profile |
| **Users** | `PUT` | `/api/users/profile` | Update profile details and social links |
| **Users** | `GET` | `/api/users/notifications` | List notifications |
| **Resumes** | `GET` | `/api/resumes` | List saved resumes |
| **Resumes** | `POST` | `/api/resumes` | Create resume |
| **Resumes** | `GET` | `/api/resumes/{id}` | Get single resume |
| **Resumes** | `PUT` | `/api/resumes/{id}` | Update resume |
| **Resumes** | `DELETE` | `/api/resumes/{id}` | Delete resume |
| **Resumes** | `POST` | `/api/resumes/{id}/duplicate` | Duplicate resume |
| **Resumes** | `POST` | `/api/resumes/upload` | Upload & parse PDF/DOCX file |
| **Jobs** | `GET` | `/api/jobs` | Get job postings |
| **Jobs** | `POST` | `/api/jobs/parse` | Extract skills from URL or text |
| **Analyze** | `POST` | `/api/analyze` | Match resume vs job, compute ATS & gaps |
| **History** | `GET` | `/api/history` | Get past analysis audit history |
| **History** | `GET` | `/api/history/{id}` | Get single analysis result details |
| **Dashboard**| `GET` | `/api/dashboard/stats` | High-level metrics for dashboard |
| **Chat** | `POST` | `/api/chat` | AI career coach assistant chat |
| **Chat** | `GET` | `/api/chat/suggestions` | AI writing suggestions for builder |
