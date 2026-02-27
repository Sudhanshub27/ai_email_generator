# ✉️ AI Email Generator

A full-stack AI-powered web application that helps users **draft professional, well-structured emails** for academic, corporate, and formal communication — while preserving **authenticity and user control**.

Instead of auto-sending emails, the app opens a **pre-filled Gmail draft** (on both desktop and mobile), allowing users to review, edit, attach files, and manually click **Send**.

---

## 🌐 Live Demo

👉 **Website:** [https://ai-email-generator-iota.vercel.app/](https://ai-email-generator-iota.vercel.app/)  
👉 **Backend API (Swagger):** [https://ai-email-generator-6af2.onrender.com/docs](https://ai-email-generator-6af2.onrender.com/docs)  

---

## ✨ Key Features

- 🧠 **AI-Powered Generation**: Transform brief points into polished emails using DeepSeek LLM via OpenRouter.
- ✍️ **Structured Output**: Automatically generates Subject, Salutation, Body, and Sign-off.
- 📧 **Direct Gmail Integration**: 
  - Subject auto-filled in Gmail **subject field**.
  - Email body cleaned and formatted correctly.
  - One-click draft creation on both **desktop and mobile**.
- 📱 **Responsive Design**: Fully optimized for mobile browsers.
- 📝 **Editable Drafts**: Review and tweak the AI's suggestions before sending.
- 🔄 **Draft History**: Remembers your last 10 generated emails locally.
- ⚡ **High Performance**: Built with Next.js 15+ and FastAPI.

---

## 🏗️ Tech Stack

- **Frontend**: Next.js (App Router), React 19, Tailwind CSS, Framer Motion, Lucide React.
- **Backend**: FastAPI, Python 3.11+, Uvicorn.
- **AI Engine**: OpenRouter API (DeepSeek Chat).
- **Deployment**: Vercel (Frontend), Render (Backend).

---

## 🚀 Local Setup

### Backend
1. Navigate to the `backend` folder:
   ```bash
   cd backend
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Create a `.env` file and add your OpenRouter API Key:
   ```env
   OPENROUTER_API_KEY=your_key_here
   ```
4. Run the server:
   ```bash
   python app.py
   ```

### Frontend
1. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env.local` file:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8080
   ```
4. Run the development server:
   ```bash
   npm run dev
   ```

---

## 📁 Project Structure

```text
ai_email_generator/
├── frontend/        # Next.js frontend
├── backend/         # FastAPI backend
└── README.md        # Project documentation
```

---

## 🧠 Design Philosophy

This project intentionally avoids fully automated sending to ensure:
- **Authenticity**: Emails come from your actual account, not a proxy.
- **Control**: You have the final say on every word sent.
- **Ethics**: Prevents accidental spam or AI hallucinations from being sent without oversight.

---

## 📄 License

MIT License - feel free to use and modify for your own projects!
