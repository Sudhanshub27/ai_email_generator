# ✉️ AI Email Generator

A full-stack AI-powered web application that helps users **draft professional, well-structured emails** for academic, corporate, and formal communication — while preserving **authenticity and user control**.

Instead of auto-sending emails, the app opens a **pre-filled Gmail draft**, allowing users to review, edit, attach files, and manually click **Send**.

---

## 🌐 Live Demo

👉 **Website:** https://ai-email-generator-neon.vercel.app/  
👉 **Backend API (Swagger):** https://ai-email-generator.up.railway.app/docs  

---

## ✨ Key Features

- 🧠 AI-generated professional email drafts
- ✍️ Clean structure: **Subject, Body, Sign-off**
- 📧 **Open in Gmail (Draft Mode)**  
  - Subject auto-filled in Gmail subject field  
  - Email body cleaned and formatted  
  - User manually sends the email (no automation misuse)
- 📝 Fully editable & copyable drafts
- ⚡ FastAPI backend with REST API
- 🎨 Modern Next.js UI with smooth animations
- ☁️ Fully deployed (Frontend + Backend)

---

## 🧠 Why “Open in Gmail” Instead of Auto-Send?

This project intentionally avoids auto-sending emails to preserve:

- ✅ Sender authenticity (email is sent from user’s Gmail)
- ✅ Academic & professional credibility
- ✅ User trust and control
- ✅ Ethical AI usage

This design mirrors real-world tools like **Grammarly** and **Notion AI**, where AI assists in writing — not impersonating users.

---

## 🏗️ Tech Stack

### Frontend
- **Next.js (App Router)**
- **React**
- **TypeScript**
- **Tailwind CSS**
- **Framer Motion**
- **React Markdown**

### Backend
- **FastAPI**
- **Python**
- **OpenRouter API**
- **DeepSeek LLM**
- **Uvicorn**

### Deployment
- **Frontend:** Vercel
- **Backend:** Railway

---

## 🔄 Application Flow

1. User provides context, dates, and key points
2. AI generates a structured email draft
3. User edits and reviews the content
4. Clicking **Open in Gmail** opens a Gmail compose window with:
   - Subject filled
   - Body formatted
5. User optionally adds attachments and manually clicks **Send**

---

## 📁 Project Structure

```text
ai_email_generator/
│
├── frontend/        # Next.js frontend
│   ├── src/
│   ├── public/
│   └── .env.local
│
├── backend/         # FastAPI backend
│   ├── app.py
│   └── requirements.txt
│
└── README.md
