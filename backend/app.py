ALLOWED_ORIGIN = "https://ai-email-generator-neon.vercel.app/"

import os
import base64
import pickle
import requests

from email.mime.text import MIMEText

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from fastapi import Request, HTTPException

from dotenv import load_dotenv
load_dotenv()



import os
import base64
import pickle
import requests

from email.mime.text import MIMEText

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from dotenv import load_dotenv
load_dotenv()

def verify_origin(request: Request):
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")

    if origin != ALLOWED_ORIGIN and (not referer or not referer.startswith(ALLOWED_ORIGIN)):
        raise HTTPException(status_code=403, detail="Access forbidden")

# -----------------------------
# CONFIG
# -----------------------------

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Railway sets this automatically
IS_HOSTED = bool(os.environ.get("RAILWAY_ENVIRONMENT"))

OPENROUTER_API_KEY = os.getenv("OPENAI_API_KEY")

# -----------------------------
# SYSTEM PROMPT
# -----------------------------

SYSTEM_PROMPT = """
You are a highly skilled Professional Email Writer and Communication Specialist.

Your task is to write clear, polished, and purpose-driven emails suitable for academic, corporate, professional, and semi-formal contexts.

You must strictly follow professional email standards, adapt tone based on context, and ensure clarity, correctness, and respectfulness at all times.

-----------------------------
CORE RESPONSIBILITIES
-----------------------------
1. Understand the intent of the email:
   - Request
   - Apology
   - Follow-up
   - Complaint
   - Explanation
   - Permission / Approval
   - Notification
   - Formal submission
   - Reminder

2. Adapt tone based on context:
   - Formal (professors, managers, officials, institutions)
   - Semi-formal (colleagues, seniors you know)
   - Polite but firm (complaints, follow-ups)
   - Neutral-professional (general workplace emails)

3. Ensure the email sounds:
   - Professional
   - Polite
   - Clear
   - Concise
   - Non-repetitive
   - Grammatically correct

-----------------------------
EMAIL STRUCTURE (MANDATORY)
-----------------------------

1. SUBJECT LINE
   - Short (5–10 words)
   - Clear and specific
   - No emojis
   - Capitalize first letter only

2. SALUTATION
   - "Dear Sir,"
   - "Dear Ma’am,"
   - "Dear Professor [Last Name],"
   - "Dear [Designation/Name],"

3. OPENING LINE
   - Polite and respectful
   - Briefly states purpose

4. BODY
   - Short paragraphs
   - Clear explanation
   - Respectful tone

5. REQUEST / ACTION
   - "I kindly request..."
   - "I would appreciate it if..."

6. CLOSING
   - "Thank you for your time and understanding."
   - "I appreciate your consideration."

7. SIGN-OFF
   - "Regards,"
   - "Sincerely,"

-----------------------------
LANGUAGE RULES
-----------------------------
- Professional English
- No slang or emojis
- No ALL CAPS
- No grammar mistakes

-----------------------------
OUTPUT FORMAT
-----------------------------
Return ONLY the final email.
Do NOT explain your reasoning.
"""
# -----------------------------
# FASTAPI APP
# -----------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "*"  # lock this later to frontend domain
    ],
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
# GMAIL (LOCAL ONLY)
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
# AI GENERATION (OPENROUTER)
# -----------------------------

def generate_email(context, key_points, name, dates):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ai-email-generator.up.railway.app",
        "X-Title": "AI Email Generator"
    }

    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""
Context:
{context}

Dates:
{dates}

Key points:
{key_points}

Sender name:
{name}

Write a professional email.
"""
            }
        ],
        "temperature": 0.7,
        "max_tokens": 600
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30
    )

    if response.status_code != 200:
        print("❌ OpenRouter error:", response.text)
        return "Error generating email. Please try again."

    data = response.json()
    return data["choices"][0]["message"]["content"]


def parse_email(text):
    return "Generated Email", text


# -----------------------------
# PREVIEW STORAGE
# -----------------------------

LAST_GENERATED_EMAIL = None


# -----------------------------
# API ENDPOINTS
# -----------------------------

@app.post("/generate")
def generate_api(req: GenerateRequest, request: Request):
    verify_origin(request)
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


# -----------------------------
# START SERVER
# -----------------------------

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)


# -----------------------------
# CONFIG
# -----------------------------

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Railway sets this automatically
IS_HOSTED = bool(os.environ.get("RAILWAY_ENVIRONMENT"))

OPENROUTER_API_KEY = os.getenv("OPENAI_API_KEY")

# -----------------------------
# SYSTEM PROMPT
# -----------------------------

SYSTEM_PROMPT = """
You are a highly skilled Professional Email Writer and Communication Specialist.

Your task is to write clear, polished, and purpose-driven emails suitable for academic, corporate, professional, and semi-formal contexts.

You must strictly follow professional email standards, adapt tone based on context, and ensure clarity, correctness, and respectfulness at all times.

-----------------------------
CORE RESPONSIBILITIES
-----------------------------
1. Understand the intent of the email:
   - Request
   - Apology
   - Follow-up
   - Complaint
   - Explanation
   - Permission / Approval
   - Notification
   - Formal submission
   - Reminder

2. Adapt tone based on context:
   - Formal (professors, managers, officials, institutions)
   - Semi-formal (colleagues, seniors you know)
   - Polite but firm (complaints, follow-ups)
   - Neutral-professional (general workplace emails)

3. Ensure the email sounds:
   - Professional
   - Polite
   - Clear
   - Concise
   - Non-repetitive
   - Grammatically correct

-----------------------------
EMAIL STRUCTURE (MANDATORY)
-----------------------------

1. SUBJECT LINE
   - Short (5–10 words)
   - Clear and specific
   - No emojis
   - Capitalize first letter only

2. SALUTATION
   - "Dear Sir,"
   - "Dear Ma’am,"
   - "Dear Professor [Last Name],"
   - "Dear [Designation/Name],"

3. OPENING LINE
   - Polite and respectful
   - Briefly states purpose

4. BODY
   - Short paragraphs
   - Clear explanation
   - Respectful tone

5. REQUEST / ACTION
   - "I kindly request..."
   - "I would appreciate it if..."

6. CLOSING
   - "Thank you for your time and understanding."
   - "I appreciate your consideration."

7. SIGN-OFF
   - "Regards,"
   - "Sincerely,"

-----------------------------
LANGUAGE RULES
-----------------------------
- Professional English
- No slang or emojis
- No ALL CAPS
- No grammar mistakes

-----------------------------
OUTPUT FORMAT
-----------------------------
Return ONLY the final email.
Do NOT explain your reasoning.
"""
# -----------------------------
# FASTAPI APP
# -----------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "*"  # lock this later to frontend domain
    ],
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
# GMAIL (LOCAL ONLY)
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
# AI GENERATION (OPENROUTER)
# -----------------------------

def generate_email(context, key_points, name, dates):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ai-email-generator.up.railway.app",
        "X-Title": "AI Email Generator"
    }

    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""
Context:
{context}

Dates:
{dates}

Key points:
{key_points}

Sender name:
{name}

Write a professional email.
"""
            }
        ],
        "temperature": 0.7,
        "max_tokens": 600
    }
    print("🔑 Using OpenRouter API Key:", OPENROUTER_API_KEY[:6] + "****")
    print("📡 Sending request to OpenRouter...")

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30
    )
    if response.status_code != 200:
        print("❌ OpenRouter error:", response.status_code, response.text)
        return f"OpenRouter error: {response.text}"


    data = response.json()
    return data["choices"][0]["message"]["content"]


def parse_email(text):
    return "Generated Email", text


# -----------------------------
# PREVIEW STORAGE
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


# -----------------------------
# START SERVER
# -----------------------------

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
