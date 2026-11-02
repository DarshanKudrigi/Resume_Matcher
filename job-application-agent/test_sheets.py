
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

credentials = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES,
)

client = gspread.authorize(credentials)

# Open the spreadsheet shared with the service account
sheet = client.open("Job Applications").sheet1

# Add a test record
sheet.append_row([
    "Test Company",
    "Software Engineer Intern",
    "https://example.com/job",
    "Not Applied",
    "2026-10-16",
])

print("Successfully connected to Google Sheets!")
