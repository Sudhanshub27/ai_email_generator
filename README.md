# ✉️ AI Email Generator

A full-stack AI-powered web application that helps users **draft professional, well-structured emails** for academic, corporate, and formal communication — while preserving **authenticity and user control**.

Instead of auto-sending emails, the app opens a **pre-filled Gmail draft** (on both desktop and mobile), allowing users to review, edit, attach files, and manually click **Send**.

---

## 🌐 Live Demo

👉 **Website:** https://ai-email-generator-neon.vercel.app/  
👉 **Backend API (Swagger):** https://ai-email-generator-6af2.onrender.com/docs  

---

## ✨ Key Features

- 🧠 AI-generated professional email drafts  
- ✍️ Clean structure: **Subject, Body, Sign-off**  
- 📧 **Open in Gmail (Draft Mode)**  
  - Subject auto-filled in Gmail **subject field**
  - Email body cleaned and formatted
  - Works seamlessly on **desktop and mobile**
  - User manually sends the email (no automation misuse)
- 📱 **Mobile-first responsive UI**
  - Fully usable on phones and tablets
  - Gmail / Mail app opens directly on mobile with draft pre-filled
- 📝 Fully editable & copyable drafts
- ⚡ FastAPI backend with REST API
- 🎨 Modern Next.js UI with smooth animations
- ☁️ Fully deployed (Frontend + Backend)

---

## 📱 Mobile Experience (Fully Supported)

The application is optimized for **mobile users**:

- 📲 Responsive UI adapts cleanly to small screens
- 📧 Clicking **Open in Gmail** on mobile:
  - Opens the **Gmail app or default Mail app**
  - Subject appears in the **Subject field**
  - Email content appears in the **Body**
- 👆 Users can edit, add attachments, and tap **Send** manually

This ensures the same high-quality experience across **desktop, Android, and iOS**.

---

## 🧠 Why “Open in Gmail” Instead of Auto-Send?

This project intentionally avoids auto-sending emails to preserve:

- ✅ Sender authenticity (email is sent from the user’s own Gmail)
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
- **Backend:** Render

---

## 🔄 Application Flow

1. User provides context, dates, and key points
2. AI generates a structured email draft
3. User edits and reviews the content
4. Clicking **Open in Gmail**:
   - Opens Gmail (desktop) or Mail/Gmail app (mobile)
   - Subject is filled in the subject field
   - Body is formatted and ready
5. User optionally adds attachments and manually clicks **Send**

---

## 📁 Project Structure

```text
ai_email_generator/
│
├── frontend/        # Next.js frontend (desktop + mobile UI)
│   ├── src/
│   ├── public/
│   └── .env.local
│
├── backend/         # FastAPI backend
│   ├── app.py
│   └── requirements.txt
│
└── README.md
