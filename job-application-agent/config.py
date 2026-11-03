import os
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY       = os.getenv("GROQ_API_KEY")
GROQ_MODEL         = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_REQUEST_DELAY = float(os.getenv("GROQ_REQUEST_DELAY", "1.5"))
GROQ_MAX_RETRIES   = int(os.getenv("GROQ_MAX_RETRIES", "3"))
GROQ_TPM_LIMIT     = int(os.getenv("GROQ_TPM_LIMIT", "8000"))
GROQ_MAX_TOKENS    = int(os.getenv("GROQ_MAX_TOKENS", "600"))
GMAIL_ADDRESS      = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RESEND_API_KEY     = os.getenv("RESEND_API_KEY")
GOOGLE_SHEET_NAME  = os.getenv("GOOGLE_SHEET_NAME", "Job Applications")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
KEYWORDS           = ["AI Engineer", "Machine Learning Engineer"]
LOCATION           = "Bengaluru"
MATCH_THRESHOLD    = 0.65
AUTO_APPLY_THRESHOLD = 0.85
