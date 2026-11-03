# ResumeMate 📄

A comprehensive full-stack platform that matches resumes against job descriptions, analyzes skill gaps, checks ATS compatibility, provides curated learning resources, features an interactive live resume builder, and includes an autonomous **Job Application Agent** to scrape and match opportunities across LinkedIn and Naukri — powered by FastAPI, PostgreSQL, Groq LLM, Playwright, and React 19.

[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=flat-square&logo=vite)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC?style=flat-square&logo=tailwind-css)](https://tailwindcss.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Groq LLM](https://img.shields.io/badge/Groq-gpt--oss--120b-F55036?style=flat-square)](https://groq.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

---

## ✨ Features

- 🎯 **AI Match Scoring:** Instant percentage match calculation between your resume and target job descriptions.
- 💼 **Find Jobs for Me (Autonomous Agent):** Automated live job search scraping up to 20 jobs from LinkedIn and Naukri, scored via Groq LLM (`openai/gpt-oss-120b`), with sliding-window TPM rate-limiting protection, dual-layer caching, and real-time 9-step Server-Sent Events (SSE) streaming.
- 🔍 **Skill Gap Analysis:** Categorized breakdown showing matched, partial, missing, and preferred technical skills.
- 📋 **ATS Checker:** Analyzes section headers, contact info integrity, layout parsability, and keyword density.
- 📚 **Learning Resources:** Recommended study paths and curated free learning resources for identified skill gaps.
- 📝 **Live Resume Builder:** Interactive dual-pane editor with live preview, 3 ATS-friendly templates (_Modern_, _Classic_, _Minimal_), AI writing suggestions, and one-click **PDF Export**.
- 📄 **Resume Upload & Parsing:** Upload PDF or DOCX resumes with automatic skills, experience, and education extraction.
- 🔐 **Authentication:** JWT-based login & signup with secure password hashing (bcrypt).
- 📊 **Google Sheets & Pipeline Tracking:** Automatically logs matched opportunities to Google Sheets with MD5 deduplication.
- 🤖 **Gemini & Groq AI Integrations:** Dual-AI capability using Google Gemini for content optimization and Groq for high-speed job discovery matching.

---

## 🛠️ Tech Stack

### Frontend

| Layer       | Technology                            |
| :---------- | :------------------------------------ |
| Framework   | React 19, Vite 8, React Router 7     |
| Styling     | Tailwind CSS 3.4, Custom Warm Palette |
| Streaming   | Fetch API + Server-Sent Events (SSE)  |
| Icons       | Lucide React                          |
| Linter      | Oxlint                                |

### Backend (`backend/`)

| Layer       | Technology                                        |
| :---------- | :------------------------------------------------ |
| Framework   | FastAPI, Uvicorn (ASGI)                           |
| Database    | PostgreSQL (asyncpg) with SQLite fallback         |
| ORM         | SQLAlchemy 2 (async)                              |
| Auth        | JWT (PyJWT) + bcrypt                              |
| File Parse  | PyPDF, python-docx, pdfplumber                    |
| AI / LLM    | Google Gemini API (optional)                      |
| Validation  | Pydantic v2, email-validator                      |

### Job Application Agent (`job-application-agent/`)

| Layer             | Technology                                      |
| :---------------- | :---------------------------------------------- |
| Scraping Engine   | Playwright (Chromium / Chrome Channel Stealth)  |
| LLM Matcher       | Groq API (`openai/gpt-oss-120b`, `gpt-oss-20b`) |
| Rate-Limit Engine | Sliding-window `TokenUsageTracker` (8,000 TPM)  |
| Caching           | In-memory `_SCORING_CACHE` + `.scoring_cache.json`|
| Tracking & Export | Google Sheets API (`gspread`, Service Account)  |
| Analytics UI      | Streamlit, Altair                               |

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** v18+ and **npm**
- **Python** 3.11+
- **Google Chrome** installed (for Playwright stealth mode)
- **PostgreSQL** 15+ _(optional — auto-falls back to SQLite)_

### 1. Clone the repository

```bash
git clone https://github.com/your-username/resume-matcher.git
cd "resume matcher"
```

### 2. Backend Setup

```bash
cd backend

# Create & activate virtual environment
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS / Linux:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend server (port 8000)
python run.py
```

API docs will be available at **http://127.0.0.1:8000/docs**.

### 3. Job Application Agent Setup

```bash
cd ../job-application-agent

# Create & activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS / Linux:
# source venv/bin/activate

# Install dependencies and browser binaries
pip install -r requirements.txt
python -m playwright install chromium

# Copy and configure .env
cp .env.example .env
# Set your GROQ_API_KEY=gsk_...
```

To run a verification test on Groq matching, rate limiting, and scrapers:
```bash
python test_tpm_fix.py
```

### 4. Frontend Setup

```bash
cd ../Frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## ⚙️ Environment Variables

### Backend (`backend/.env`)

| Variable             | Description                                        | Default              |
| :------------------- | :------------------------------------------------- | :------------------- |
| `PROJECT_NAME`       | App name shown in API docs                         | `ResumeMate API`     |
| `PORT`               | Backend server port                                | `8000`               |
| `SECRET_KEY`         | JWT signing secret (**change in production**)      | —                    |
| `DATABASE_URL`       | Async DB URL (e.g. `postgresql+asyncpg://...`)     | —                    |
| `FALLBACK_TO_SQLITE` | Use SQLite if PostgreSQL is unavailable            | `True`               |
| `GEMINI_API_KEY`     | Google Gemini API key (optional)                   | —                    |

### Job Application Agent (`job-application-agent/.env`)

| Variable             | Description                                        | Default              |
| :------------------- | :------------------------------------------------- | :------------------- |
| `GROQ_API_KEY`       | Groq Cloud API key                                 | **Required**         |
| `GROQ_MODEL`         | Primary LLM model for resume matching              | `openai/gpt-oss-120b`|
| `GROQ_TPM_LIMIT`     | Tokens Per Minute ceiling for request throttling   | `8000`               |
| `GROQ_MAX_TOKENS`    | Output token limit per completion                  | `600`                |
| `GROQ_REQUEST_DELAY` | Sequential pause between requests (seconds)        | `1.5`                |
| `GROQ_MAX_RETRIES`   | Controlled retries on rate limits (429)            | `3`                  |
| `GOOGLE_SHEET_NAME`  | Google Sheets document name                        | `Job Applications`   |

---

## 📁 Project Structure

```plaintext
resume matcher/
├── Frontend/                       # React 19 single-page application
│   ├── src/
│   │   ├── components/             # Reusable UI (ATSChecker, ResumeUpload, JobRecommendations, etc.)
│   │   ├── context/                # AppContext & ThemeContext for global state
│   │   ├── data/                   # Mock data & sample templates
│   │   ├── pages/                  # Route views (Dashboard, Analyzer, Results, FindJobs, Builder)
│   │   ├── services/               # API client & SSE stream handler (api.js)
│   │   ├── App.jsx                 # Route configurations
│   │   └── main.jsx                # App entry point
│   ├── package.json
│   └── vite.config.js
│
├── backend/                        # FastAPI REST API
│   ├── app/
│   │   ├── models/                 # SQLAlchemy models (User, Resume, JobPosting)
│   │   ├── routers/                # API routes (auth, resumes, jobs, analyze, recommendations)
│   │   ├── schemas/                # Pydantic validation schemas
│   │   ├── services/               # Parsing, ATS analysis, skill extraction, recommendation
│   │   ├── config.py               # Backend settings
│   │   └── database.py             # Database session manager
│   ├── main.py                     # FastAPI application instance
│   ├── run.py                      # Server launcher
│   └── requirements.txt
│
├── job-application-agent/          # Autonomous Job Application Agent
│   ├── scraper/                    # Playwright scrapers for LinkedIn & Naukri
│   ├── matcher/                    # Groq LLM scoring, prompt compaction, TPM rate limiter
│   ├── tracker/                    # Models & Google Sheets sync (gspread)
│   ├── dashboard/                  # Streamlit metrics dashboard
│   ├── agent_service.py            # 9-Step SSE streaming service for Find Jobs
│   ├── config.py                   # Agent settings & model configurations
│   ├── main.py                     # CLI pipeline runner
│   ├── resume.txt                  # Plain text resume for CLI mode
│   └── test_tpm_fix.py             # Automated rate limiting & token compaction tests
│
└── README.md
```

---

## 🔌 Key API Endpoints

| Method | Endpoint                        | Description                                  |
| :----- | :------------------------------ | :------------------------------------------- |
| GET    | `/api/health`                   | System health & active database status       |
| POST   | `/api/auth/login`               | Authenticate user and issue JWT              |
| POST   | `/api/auth/signup`              | Register a new user account                  |
| POST   | `/api/resumes/upload`           | Upload & parse PDF/DOCX resume file          |
| POST   | `/api/analyze`                  | Full resume ↔ job match & ATS analysis       |
| POST   | `/api/recommendations/match`    | Match resume against multiple job postings   |
| POST   | `/api/recommendations/stream`   | Stream job recommendations with real-time SSE|
| POST   | `/api/agent/stream-jobs`        | Stream autonomous LinkedIn + Naukri discovery|
| GET    | `/api/dashboard`                | Retrieve candidate summary statistics        |

---

## 📜 Available Scripts

### Frontend (`Frontend/`)

```bash
npm run dev      # Launch React dev server (http://localhost:5173)
npm run build    # Production build
npm run preview  # Preview production build locally
npm run lint     # Lint using Oxlint
```

### Backend (`backend/`)

```bash
python run.py                   # Run FastAPI dev server with hot reload
python test_all_endpoints.py    # Run API endpoint test suite
```

### Job Application Agent (`job-application-agent/`)

```bash
python main.py                  # Run standalone scraping & scoring pipeline
streamlit run dashboard/app.py  # Launch Streamlit analytics dashboard
python test_tpm_fix.py          # Run TPM rate limiting & caching tests
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
