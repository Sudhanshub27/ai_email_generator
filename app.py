import os
import base64
import pickle
from email.mime.text import MIMEText

import gradio as gr
from openai import OpenAI
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# -----------------------------
# CONFIG
# -----------------------------

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
IS_HOSTED = os.environ.get("SPACE_ID") is not None  # Hugging Face detection

# Ollama (local)
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
# GMAIL LOGIC (LOCAL ONLY)
# -----------------------------

def send_gmail(to_email, subject, body):
    if IS_HOSTED:
        return "❌ Email sending is disabled on hosted version."

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
# PREVIEW → SEND FLOW
# -----------------------------

LAST_GENERATED_EMAIL = None


def preview_email(context, key_points, name, dates):
    global LAST_GENERATED_EMAIL
    LAST_GENERATED_EMAIL = generate_email(context, key_points, name, dates)
    return LAST_GENERATED_EMAIL


def send_previewed_email(to_email):
    global LAST_GENERATED_EMAIL

    if LAST_GENERATED_EMAIL is None:
        return "❌ Please generate an email first."

    subject, body = parse_email(LAST_GENERATED_EMAIL)
    return send_gmail(to_email, subject, body)


# -----------------------------
# GRADIO UI
# -----------------------------

with gr.Blocks(title="AI Email Generator") as demo:

    gr.Markdown("## ✉️ AI Email Generator")

    context = gr.Textbox(
        label="What is the email about?",
        placeholder="e.g., Academic lab absence"
    )

    dates = gr.Textbox(
        label="Relevant Dates",
        placeholder="e.g., Thursday, 12 Sept 2025"
    )

    key_points = gr.Textbox(
        label="Key Points",
        lines=5,
        placeholder="- Reason\n- Request\n- Submission plan"
    )

    name = gr.Textbox(
        label="Your Name",
        placeholder="e.g., Sudhanshu Batra"
    )

    to_email = gr.Textbox(
        label="Send To (Email)",
        placeholder="example@gmail.com"
    )

    with gr.Row():
        generate_btn = gr.Button("🔄 Generate / Preview")
        send_btn = gr.Button("📨 Send Email")

    preview = gr.Markdown(label="📄 Email Preview")
    status = gr.Markdown()

    generate_btn.click(
        fn=preview_email,
        inputs=[context, key_points, name, dates],
        outputs=preview
    )

    send_btn.click(
        fn=send_previewed_email,
        inputs=to_email,
        outputs=status
    )

demo.launch(inbrowser=not IS_HOSTED)
