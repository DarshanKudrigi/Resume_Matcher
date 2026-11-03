# Job Application Agent

An autonomous AI-powered job search agent that scrapes job listings from LinkedIn and Naukri, scores them against candidate resumes using Groq's high-throughput LLMs (`openai/gpt-oss-120b`), manages TPM rate limits with sliding-window throttling, and tracks opportunities in Google Sheets and the Resume Matcher frontend.

---

## Architecture & Workflow

```
┌─────────────────────────────────┐      ┌───────────────────────────────┐
│        Multi-Portal Scraping    │      │    Token-Optimized Matching   │
│  • LinkedIn (28s, DOMContentLoaded)├───►│  • Resume Compaction (~350t) │
│  • Naukri (Chrome Stealth Mode) │      │  • JD Boilerplate Pruning    │
│  • 10 LinkedIn + 10 Naukri (20) │      │  • Groq: openai/gpt-oss-120b  │
└─────────────────────────────────┘      └──────────────┬────────────────┘
                                                        │
                      ┌─────────────────────────────────┴──────────────────────────────┐
                      ▼                                                                ▼
┌──────────────────────────────────────────────┐      ┌──────────────────────────────────────────────┐
│       Sliding-Window TPM Rate Limiter        │      │          Dual-Layer Caching Engine           │
│  • 8,000 TPM Budget Tracker (Rolling 60s)    │      │  • In-Memory Cache + .scoring_cache.json     │
│  • max_tokens = 600 Output Cap               │      │  • Sub-2ms instant cache hits                │
│  • Single Retry Loop + Retry-After Backoff   │      │  • Only retries failed/unscored jobs         │
└──────────────────────┬───────────────────────┘      └──────────────────────┬───────────────────────┘
                       │                                                     │
                       ▼                                                     ▼
┌──────────────────────────────────────────────┐      ┌──────────────────────────────────────────────┐
│          Resume Matcher Frontend (React)     │      │        Google Sheets & Streamlit UI          │
│  • 9-Step Real-time SSE Stream (agent_service│      │  • Batch write with MD5 deduplication        │
│  • Direct Match % & Skill Gap Badges         │      │  • Status pipeline (applied, interview, etc) │
└──────────────────────────────────────────────┘      └──────────────────────────────────────────────┘
```

1. **Scraper Engine**: Playwright drives Chromium/System Chrome with anti-detection evasions to scrape active job cards from LinkedIn and Naukri across Bangalore (configurable).
2. **Prompt Compactor**: Compresses resumes (removing personal emails/phones/addresses/noise) and prunes JD boilerplate (EEO statements, benefits/perks, recruiter notices) to cut token consumption by >50%.
3. **Groq LLM Matcher**: Evaluates candidates against JDs using `openai/gpt-oss-120b` (fallback: `openai/gpt-oss-20b`) with a structured 7-field JSON schema (`score`, `matched_skills`, `missing_skills`, `recommendation`, `reason`, `experience_required`, `experience_match`).
4. **TPM Budget Protection**: `TokenUsageTracker` maintains a 60-second sliding window against the 8,000 TPM limit. When near capacity, it dynamically pauses to prevent HTTP 429 errors.
5. **Dual-Layer Caching**: Successfully scored jobs are cached in memory and persisted to `.scoring_cache.json` using stable hashes. Re-evaluations cost 0 tokens and take <2ms.
6. **Multi-Channel Delivery**: Streams real-time Server-Sent Events (SSE) to the Resume Matcher React frontend, exports to Google Sheets (`gspread`), or renders inside a local Streamlit dashboard.

---

## Key Features

- **Multi-Portal Scraping**: Concurrently scrapes up to 10 jobs from LinkedIn and 10 from Naukri (20 jobs max total).
- **Stealth Anti-Bot Bypass**: Naukri scraper uses system Chrome channels and stealth scripts to circumvent Akamai 403 blocks.
- **Resilient Description Fetching**: LinkedIn scraper uses 28s timeouts with `domcontentloaded` wait states and multi-selector fallbacks.
- **Production Groq Migration**: Migrated from decommissioned Llama models to official Groq `openai/gpt-oss-120b` (primary) and `openai/gpt-oss-20b` (fallback).
- **TPM Rate-Limit Protection**: Sliding-window token tracking, `max_tokens=600`, and single controlled retry loop (`max_retries=0` in SDK) respecting HTTP 429 `Retry-After` headers.
- **Persistent Caching**: Preserves completed job scores across server restarts; retries only jobs whose scoring failed.
- **Job Failure Isolation**: If a single job fails scoring after 3 retries, it is assigned a safe fallback score (`0.5`) and preserved so the other 19 jobs complete without interruption.
- **Google Sheets Sync**: Automatic batch upload of scored jobs with MD5 deduplication on job URLs.
- **Real-Time SSE Streaming**: 9 distinct discovery steps streamed live to the React UI via `agent_service.py`.

---

## Project Structure

```
job-application-agent/
├── matcher/
│   ├── __init__.py
│   └── resume_matcher.py        # Token tracker, prompt compaction, Groq scoring & caching
├── scraper/
│   ├── __init__.py
│   ├── base_scraper.py          # Abstract base scraper
│   ├── linkedin_scraper.py      # LinkedIn Playwright scraper (28s, DOMContentLoaded)
│   └── naukri_scraper.py        # Naukri scraper (Chrome channel, anti-detection)
├── tracker/
│   ├── __init__.py
│   ├── models.py                # Job dataclass with stable MD5 ID hashing
│   └── sheets_tracker.py        # Google Sheets read/write with socket timeout
├── dashboard/
│   ├── __init__.py
│   ├── app.py                   # Streamlit analytics dashboard
│   ├── components.py            # Dashboard charts & UI widgets
│   └── styles.py                # Custom CSS styling
├── agent_service.py             # 9-Step SSE streaming service for Resume Matcher frontend
├── config.py                    # Central configuration & environment variables
├── main.py                      # Standalone CLI pipeline runner
├── resume.txt                   # Local plain text resume for CLI mode
├── requirements.txt             # Python dependencies
├── .env                         # Secrets & API credentials
├── .scoring_cache.json          # Persistent scoring cache (auto-generated)
└── test_tpm_fix.py              # Automated test suite for TPM limits & token compaction
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Language & Runtime** | Python 3.11+, Asyncio |
| **Web Scraping** | Playwright (Chromium / Chrome Channel) |
| **LLM Inference** | Groq API (`openai/gpt-oss-120b`, `openai/gpt-oss-20b`) |
| **Rate-Limit Control** | Sliding-window `TokenUsageTracker` (8,000 TPM ceiling) |
| **Caching** | Dual-layer (In-memory + `.scoring_cache.json` disk file) |
| **Cloud Tracking** | Google Sheets API (`gspread`, OAuth2 Service Account) |
| **UI Dashboard** | Streamlit, Altair |
| **Web Integration** | FastAPI / Starlette SSE streaming |

---

## Configuration (`.env`)

Create a `.env` file inside `job-application-agent/`:

```env
# Groq API Configuration
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
GROQ_TPM_LIMIT=8000
GROQ_MAX_TOKENS=600
GROQ_REQUEST_DELAY=1.5
GROQ_MAX_RETRIES=3

# Google Sheets Tracker (Optional)
GOOGLE_SHEET_NAME=Job Applications
GOOGLE_CREDENTIALS_PATH=credentials.json

# Notification Settings (Optional)
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
RESEND_API_KEY=your_resend_api_key
```

### Configuration Options

| Variable | Description | Default |
|---|---|---|
| `GROQ_API_KEY` | Your Groq Cloud API key | **Required** |
| `GROQ_MODEL` | Primary LLM model for resume matching | `openai/gpt-oss-120b` |
| `GROQ_TPM_LIMIT` | Groq Tokens Per Minute limit | `8000` |
| `GROQ_MAX_TOKENS` | Max output tokens per completion | `600` |
| `GROQ_REQUEST_DELAY`| Minimum delay (seconds) between sequential requests | `1.5` |
| `GROQ_MAX_RETRIES` | Max retries per job on rate limit / error | `3` |
| `MATCH_THRESHOLD` | Minimum score (0.0–1.0) to qualify as a match | `0.65` |
| `AUTO_APPLY_THRESHOLD` | Score threshold for high-priority opportunities | `0.85` |

---

## Setup & Installation

### 1. Create and Activate Virtual Environment

```bash
cd "job-application-agent"

# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies & Playwright Browsers

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

---

## Usage

### Mode A: Integrated Frontend (Resume Matcher)
The agent integrates directly with the Resume Matcher React application. When you click **"Find Jobs for Me"** in the UI:
1. The frontend initiates an SSE connection to `/api/agent/stream-jobs`.
2. The agent executes the 9-step discovery pipeline in real time.
3. Opportunities are scored, ranked, and rendered directly with skill badges, match percentages, and direct apply links.

### Mode B: Standalone CLI Pipeline

Ensure `resume.txt` contains your plain text resume:

```bash
python main.py
```

Execution output:
- Scrapes up to 10 jobs from LinkedIn and 10 from Naukri.
- Scores all retrieved opportunities against `resume.txt`.
- Filters jobs by experience requirement ($\le 2$ years) and score threshold ($\ge 65\%$).
- Appends qualified opportunities to your Google Sheet.

### Mode C: Streamlit Analytics Dashboard

```bash
python -m streamlit run dashboard/app.py
```

Access the dashboard at `http://localhost:8501` to view:
- Metrics breakdown (total tracked, apply count, average match score).
- Score distribution charts and recommendation breakdowns.
- Interactive job pipeline with status management (`new`, `applied`, `interview`, `offer`, `rejected`).
- One-click agent execution and Google Sheets reset.

---

## Testing & Verification

Run the dedicated TPM rate-limiting and token compaction test suite:

```bash
python test_tpm_fix.py
```

Tests included:
1. **Prompt Compaction**: Verifies resume compression and JD boilerplate stripping.
2. **Sliding-Window Throttling**: Tests dynamic pausing when approaching the 8,000 TPM limit.
3. **Single Retry Recovery**: Verifies `max_retries=0` in SDK and controlled recovery on HTTP 429 `Retry-After`.
4. **Dual Caching**: Tests <2ms instant cache hits and verifies only failed jobs are retried.
5. **20-Job Batch Execution**: Validates full 20-job batch processing without unhandled rate-limit exceptions.
