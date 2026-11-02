# ResumeMate 📄

A full-stack application that matches resumes against job descriptions, analyzes skill gaps, checks ATS compatibility, provides curated learning resources, and includes an interactive resume builder — powered by a FastAPI + PostgreSQL backend and a React frontend.

[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=flat-square&logo=vite)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC?style=flat-square&logo=tailwind-css)](https://tailwindcss.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

---

## ✨ Features

- 🎯 **AI Match Scoring:** Instant percentage match calculation between your resume and target job descriptions.
- 🔍 **Skill Gap Analysis:** Categorized breakdown showing matched, partial, and missing technical skills.
- 📋 **ATS Checker:** Analyzes section headers, contact info integrity, layout parsability, and keyword density.
- 📚 **Learning Resources:** Recommended study paths and curated free learning resources for missing skills.
- 📝 **Live Resume Builder:** Interactive dual-pane editor with live preview, 3 ATS-friendly templates (_Modern_, _Classic_, _Minimal_), AI writing suggestions, and one-click **PDF Export**.
- 📄 **Resume Upload & Parsing:** Upload PDF or DOCX resumes — the backend extracts and parses text automatically.
- 🔐 **Authentication:** JWT-based login & signup with secure password hashing (bcrypt).
- 🤖 **Gemini AI Integration:** Optional Google Gemini API support for deep LLM-powered analysis; falls back to a built-in NLP & rules engine when no API key is set.

---

## 🛠️ Tech Stack

### Frontend

| Layer       | Technology                            |
| :---------- | :------------------------------------ |
| Framework   | React 19, Vite 8, React Router 7     |
| Styling     | Tailwind CSS 3.4, Custom Warm Palette |
| Icons       | Lucide React                          |
| Linter      | Oxlint                                |

### Backend

| Layer       | Technology                                        |
| :---------- | :------------------------------------------------ |
| Framework   | FastAPI, Uvicorn (ASGI)                           |
| Database    | PostgreSQL (asyncpg) with SQLite fallback         |
| ORM         | SQLAlchemy 2 (async)                              |
| Auth        | JWT (PyJWT) + bcrypt                              |
| File Parse  | PyPDF, python-docx                                |
| AI / LLM    | Google Gemini API (optional)                      |
| Validation  | Pydantic v2, email-validator                      |

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** v18+ and **npm**
- **Python** 3.11+
- **PostgreSQL** 15+ _(optional — the backend auto-falls back to SQLite)_

### 1. Clone the repository

```bash
git clone https://github.com/your-username/resume-matcher.git
cd "resume matcher"
```

### 2. Backend Setup

```bash
# Navigate to the backend
cd backend

# Create & activate a virtual environment
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS / Linux:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your PostgreSQL credentials and optional Gemini API key

# Start the backend server (hot-reload enabled)
python run.py
```

The API will be live at **http://127.0.0.1:8000** with interactive Swagger docs at **http://127.0.0.1:8000/docs**.

### 3. Frontend Setup

```bash
# From the project root, navigate to the frontend
cd Frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## ⚙️ Environment Variables

Create a `.env` file inside `backend/` (use `.env.example` as a template):

| Variable                     | Description                                        | Default                     |
| :--------------------------- | :------------------------------------------------- | :-------------------------- |
| `PROJECT_NAME`               | App name shown in API docs                         | `ResumeMate API`            |
| `PORT`                       | Backend server port                                | `8000`                      |
| `SECRET_KEY`                 | JWT signing secret (**change in production**)      | —                           |
| `DB_USER`                    | PostgreSQL username                                | `postgres`                  |
| `DB_PASSWORD`                | PostgreSQL password                                | `postgres`                  |
| `DB_HOST`                    | PostgreSQL host                                    | `localhost`                 |
| `DB_PORT`                    | PostgreSQL port                                    | `5432`                      |
| `DB_NAME`                    | PostgreSQL database name                           | `resume_analyzer_db`        |
| `DATABASE_URL`               | Full async DB URL (overrides individual DB_* vars) | —                           |
| `FALLBACK_TO_SQLITE`         | Use SQLite if PostgreSQL is unavailable            | `True`                      |
| `GEMINI_API_KEY`             | Google Gemini API key (optional)                   | —                           |

---

## 📁 Project Structure

```plaintext
resume matcher/
├── Frontend/                   # React single-page application
│   ├── src/
│   │   ├── components/         # Reusable UI (ATSChecker, MatchScore, ResumeForm, etc.)
│   │   ├── context/            # AppContext & ThemeContext for global state
│   │   ├── data/               # Mock sample data for jobs, profiles & AI suggestions
│   │   ├── pages/              # Route views (Dashboard, Analyzer, Results, Builder, etc.)
│   │   ├── services/           # API client (api.js)
│   │   ├── App.jsx             # Routes & app wrapper
│   │   ├── main.jsx            # Entry point
│   │   └── index.css           # Tailwind directives & theme styles
│   ├── package.json
│   └── vite.config.js
│
├── backend/                    # FastAPI REST API
│   ├── app/
│   │   ├── models/             # SQLAlchemy models (User, Resume, JobPosting)
│   │   ├── routers/            # API route handlers (auth, resumes, jobs, analyze, etc.)
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # Business logic (AI, matching, parsing, OCR, auth)
│   │   ├── config.py           # App settings (pydantic-settings)
│   │   └── database.py         # Async SQLAlchemy engine & session setup
│   ├── data/                   # SQLite database file (auto-generated)
│   ├── uploads/                # Uploaded resume files
│   ├── main.py                 # FastAPI app instance, lifespan & middleware
│   ├── run.py                  # Uvicorn dev server launcher
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Environment variable template
│
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint              | Description                      |
| :----- | :-------------------- | :------------------------------- |
| GET    | `/`                   | Root — app info & status         |
| GET    | `/api/health`         | Health check (DB type, AI flag)  |
| POST   | `/api/auth/login`     | Login (returns JWT)              |
| POST   | `/api/auth/signup`    | Register a new user              |
| GET    | `/api/users/me`       | Get current user profile         |
| PUT    | `/api/users/me`       | Update current user profile      |
| GET    | `/api/resumes`        | List user resumes                |
| POST   | `/api/resumes`        | Create / save a resume           |
| POST   | `/api/resumes/upload` | Upload a PDF / DOCX resume       |
| GET    | `/api/jobs`           | List job postings                |
| POST   | `/api/jobs`           | Create a job posting             |
| POST   | `/api/analyze`        | Run resume ↔ job match analysis  |
| GET    | `/api/dashboard`      | Dashboard summary stats          |
| POST   | `/api/chat`           | AI chat for resume advice        |

---

## 📜 Available Scripts

### Frontend (`Frontend/`)

| Command            | Description                                     |
| :----------------- | :---------------------------------------------- |
| `npm run dev`      | Runs the dev server at `localhost:5173`          |
| `npm run build`    | Builds the project for production               |
| `npm run preview`  | Previews the production build locally            |
| `npm run lint`     | Lints the codebase using Oxlint                  |

### Backend (`backend/`)

| Command                        | Description                                  |
| :----------------------------- | :------------------------------------------- |
| `python run.py`                | Starts FastAPI with hot-reload               |
| `python init_db.py`            | Initializes / resets the database             |
| `python test_all_endpoints.py` | Runs the endpoint test suite                  |

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
