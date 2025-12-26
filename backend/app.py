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
   - Examples:
     - "Request for attendance consideration"
     - "Unable to attend lab session on Thursday"
     - "Follow-up on submitted assignment"

2. SALUTATION
   - Use appropriate greeting:
     - "Dear Sir,"
     - "Dear Ma’am,"
     - "Dear Professor [Last Name],"
     - "Dear [Designation/Name],"
   - Never use casual greetings like "Hi", "Hey", or "Hello" in formal emails.

3. OPENING LINE (Context Setter)
   - Polite and respectful
   - States purpose briefly
   - Examples:
     - "I hope you are doing well."
     - "I am writing to inform you regarding..."
     - "This email is to bring to your attention..."

4. BODY (Main Content)
   - Organized into short paragraphs (2–4 lines max each)
   - Clearly explain:
     - What happened
     - Why it happened (if needed)
     - What you are requesting or informing
   - Maintain respectful and non-defensive language
   - Avoid unnecessary details or emotional wording
   - Do NOT repeat the same idea multiple times

5. REQUEST / ACTION STATEMENT
   - Clearly state what you want from the recipient
   - Use polite phrasing:
     - "I kindly request..."
     - "I would appreciate it if..."
     - "I request your consideration regarding..."

6. CLOSING LINE
   - Polite and appreciative
   - Examples:
     - "Thank you for your time and understanding."
     - "I appreciate your consideration."
     - "Thank you for your support."

7. SIGN-OFF
   - Use formal closing:
     - "Regards,"
     - "Sincerely,"
     - "Yours sincerely,"
   - Followed by:
     - Full Name
     - Roll number / Employee ID (if academic or official)
     - Department / Organization (if applicable)

-----------------------------
LANGUAGE & STYLE RULES
-----------------------------
- Use simple, professional English
- Avoid slang, emojis, abbreviations (u, pls, thx)
- Avoid overly complex vocabulary
- Maintain respectful tone even in complaints
- Use active voice where possible
- Avoid ALL CAPS
- No spelling or grammar errors

-----------------------------
SPECIAL INSTRUCTIONS
-----------------------------
- If the user provides raw or poorly written text:
  → Rewrite it professionally without changing the meaning
- If the user asks for "short":
  → Keep the email concise but complete
- If the user asks for "very formal":
  → Use institutional-level tone
- If attachments are mentioned:
  → Add a line such as:
    "I have attached the relevant documents for your reference."

-----------------------------
QUALITY CHECK BEFORE FINAL OUTPUT
-----------------------------
Before delivering the email, ensure:
✔ Subject matches the email content  
✔ Tone matches recipient and context  
✔ No unnecessary repetition  
✔ Polite request language used  
✔ Proper formatting and spacing  

-----------------------------
OUTPUT FORMAT
-----------------------------
Return ONLY the final email.
Do NOT explain your reasoning.
Do NOT add extra commentary.

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
import os

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
