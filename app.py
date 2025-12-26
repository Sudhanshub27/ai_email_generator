import os
import base64
import pickle
from email.mime.text import MIMEText

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from openai import OpenAI
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# -----------------------------
# CONFIG
# -----------------------------

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Detect hosted environment (for future)
IS_HOSTED = os.environ.get("VERCEL") or os.environ.get("RENDER")

# Ollama (local LLM)
openai = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

SYSTEM_PROMPT = """
You are an intelligent email-writing assistant.

STRICT RULES:
- Always output Markdown
- Always include:
  ## Subject
  ## Email Body
"""

# -----------------------------
# FASTAPI APP
# -----------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# REQUEST MODELS
# -----------------------------

class GenerateRequest(BaseModel):
    context: str
    dates: str
    key_points: str
    name: str


class SendRequest(BaseModel):
    to_email: str


# -----------------------------
# GMAIL (LOCAL / DEMO ONLY)
# -----------------------------

def send_gmail(to_email, subject, body):
    if IS_HOSTED:
        return "❌ Email sending disabled on hosted version."

    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("gmail", "v1", credentials=creds)

    message = MIMEText(body.replace("\n", "<br>"), "html")
    message["to"] = to_email
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()

    return "✅ Email sent successfully!"


# -----------------------------
# AI GENERATION
# -----------------------------

def generate_email(context, key_points, name, dates):
    user_prompt = f"""
Write a professional email using the details below.

Context:
{context}

Dates:
{dates}

Key points:
{key_points}

Sender name:
{name}

Naturally include the dates.
"""
    response = openai.chat.completions.create(
        model="llama3.2",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content


def parse_email(md_text):
    subject = "No Subject"
    body = md_text

    if "## Subject" in md_text:
        part = md_text.split("## Subject", 1)[1]
        if "## Email Body" in part:
            subject = part.split("## Email Body", 1)[0].strip()
            body = part.split("## Email Body", 1)[1].strip()

    return subject, body


# -----------------------------
# PREVIEW STORAGE (MVP)
# -----------------------------

LAST_GENERATED_EMAIL = None


# -----------------------------
# API ENDPOINTS
# -----------------------------

@app.post("/generate")
def generate_api(req: GenerateRequest):
    global LAST_GENERATED_EMAIL

    LAST_GENERATED_EMAIL = generate_email(
        req.context,
        req.key_points,
        req.name,
        req.dates
    )

    return {"email": LAST_GENERATED_EMAIL}


@app.post("/send")
def send_api(req: SendRequest):
    if LAST_GENERATED_EMAIL is None:
        return {"error": "Generate email first"}

    subject, body = parse_email(LAST_GENERATED_EMAIL)
    result = send_gmail(req.to_email, subject, body)

    return {"status": result}
