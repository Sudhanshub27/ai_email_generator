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

# -----------------------------
# CONFIG
# -----------------------------

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Railway sets this automatically
IS_HOSTED = bool(os.environ.get("RAILWAY_ENVIRONMENT"))

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# -----------------------------
# SYSTEM PROMPT
# -----------------------------

SYSTEM_PROMPT = """
You are a highly skilled Professional Email Writer and Communication Specialist.

Your task is to write clear, polished, and purpose-driven emails suitable for academic, corporate, professional, and semi-formal contexts.

You must strictly follow professional email standards, adapt tone based on context, and ensure clarity, correctness, and respectfulness at all times.

-----------------------------
TONE GUIDELINES
-----------------------------
- **Formal**: Use sophisticated vocabulary, avoid contractions, and maintain a respectful distance.
- **Semi-Formal**: Professional but slightly more approachable, suitable for colleagues.
- **Friendly/Casual**: Cooperative and warm, while remaining professional.
- **Urgent**: Concise, direct, and emphasizes the need for a quick response.
- **Persuasive**: Compelling language used to influence or convince the recipient.
- **Polite/Humble**: Softened language, often for requests or apologies.

-----------------------------
EMAIL STRUCTURE (MANDATORY)
-----------------------------

1. SUBJECT LINE
   - Short (5–10 words)
   - Clear and specific
   - No emojis
   - Capitalize first letter only

2. SALUTATION
   - Appropriate for the chosen tone and recipient.

3. OPENING LINE
   - Polite and respectful
   - Briefly states purpose

4. BODY
   - Short paragraphs
   - Clear explanation
   - Tone-appropriate language

5. REQUEST / ACTION
   - Clear and professional call to action.

6. CLOSING
   - Professional closing statement.

7. SIGN-OFF
   - "Regards,", "Sincerely,", "Best,", etc.

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
Start with "Subject: [Your Subject Line]" followed by the email body.
Do NOT explain your reasoning.
Do NOT use markdown bolding (like **) in the email content.
"""
# -----------------------------
# FASTAPI APP
# -----------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3010",
        "http://localhost:3015",
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
    tone: str = "Formal"
    template: str = "General"


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

def generate_email(context, key_points, name, dates, tone, template):
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
Context: {context}
Dates: {dates}
Key points: {key_points}
Sender name: {name}
Tone: {tone}
Template Type: {template}

Write a professional email following the requested tone and template style.
"""
            }
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }

    print(f"🚀 Sending request to OpenRouter with tone: {tone}, template: {template}")
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ OpenRouter error (Status {response.status_code}): {response.text}")
            return f"Error: AI service returned status {response.status_code}. {response.text[:100]}"

        data = response.json()
        if "choices" not in data or not data["choices"]:
            print(f"❌ Unexpected OpenRouter response structure: {data}")
            return "Error: Received unexpected response from AI service."
            
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ Exception during OpenRouter request: {str(e)}")
        return f"Error: Request failed. {str(e)}"


def parse_email(text):
    import re
    # Remove extra starts (markdown bolding)
    text = text.replace("**", "")
    
    subject = "Generated Email"
    body = text

    # Robust subject extraction
    subject_match = re.search(r"^Subject:\s*(.*)$", text, re.IGNORECASE | re.MULTILINE)
    if subject_match:
        subject = subject_match.group(1).strip()
        # Remove the subject line from the body
        body = text.replace(subject_match.group(0), "").strip()
    
    return subject, body


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
        req.dates,
        req.tone,
        req.template
    )

    return {"email": LAST_GENERATED_EMAIL}


@app.get("/preview")
def preview_api():
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
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port)


