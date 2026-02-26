"use client";

import { useState, useMemo, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles,
  Copy,
  Check,
  RotateCcw,
  Mail,
  History,
  Trash2,
  ExternalLink,
  ChevronDown,
  Layout,
  MessageSquare
} from "lucide-react";

// Tones and Templates
const TONES = [
  "Formal",
  "Semi-Formal",
  "Friendly/Casual",
  "Urgent",
  "Persuasive",
  "Polite/Humble"
];

const TEMPLATES = [
  "General",
  "Leave Application",
  "Job Application",
  "Meeting Request",
  "Follow-up",
  "Resignation",
  "Thank You Note"
];

interface EmailHistory {
  id: string;
  timestamp: number;
  subject: string;
  body: string;
  context: string;
}

export default function Home() {
  const [context, setContext] = useState("");
  const [dates, setDates] = useState("");
  const [keyPoints, setKeyPoints] = useState("");
  const [name, setName] = useState("");
  const [toEmail, setToEmail] = useState("");
  const [tone, setTone] = useState("Formal");
  const [template, setTemplate] = useState("General");

  const [preview, setPreview] = useState("");
  const [editableDraft, setEditableDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [history, setHistory] = useState<EmailHistory[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  // Load history from LocalStorage
  useEffect(() => {
    const savedHistory = localStorage.getItem("email_history");
    if (savedHistory) {
      try {
        setHistory(JSON.parse(savedHistory));
      } catch (e) {
        console.error("Failed to parse history", e);
      }
    }
  }, []);

  // Save history to LocalStorage
  const saveToHistory = (email: string, ctx: string) => {
    const { subject, body } = extractSubjectAndBody(email);
    const newEntry: EmailHistory = {
      id: Math.random().toString(36).substr(2, 9),
      timestamp: Date.now(),
      subject,
      body,
      context: ctx
    };
    const updatedHistory = [newEntry, ...history].slice(0, 10); // Keep last 10
    setHistory(updatedHistory);
    localStorage.setItem("email_history", JSON.stringify(updatedHistory));
  };

  const deleteHistoryItem = (id: string) => {
    const updatedHistory = history.filter(item => item.id !== id);
    setHistory(updatedHistory);
    localStorage.setItem("email_history", JSON.stringify(updatedHistory));
  };

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem("email_history");
  };

  const showToast = (message: string, type: "success" | "error" = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const isValidEmail = (email: string) =>
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  const generateEmail = async () => {
    if (!context || !name) {
      showToast("Please fill in the purpose and your name.", "error");
      return;
    }

    setLoading(true);
    setCopied(false);

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/generate`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            context,
            dates,
            key_points: keyPoints,
            name,
            tone,
            template
          }),
        }
      );

      const data = await res.json();
      if (data.email) {
        setPreview(data.email);
        setEditableDraft(data.email);
        saveToHistory(data.email, context);
        showToast("Email generated successfully!");
      } else {
        throw new Error("Empty response");
      }
    } catch (e) {
      console.error("Generation failed", e);
      showToast("Failed to generate email. Is the backend running?", "error");
    } finally {
      setLoading(false);
    }
  };

  const extractSubjectAndBody = (text: string) => {
    // Remove extra stars from anywhere in the text
    const cleanText = text.replace(/\*\*/g, "").trim();

    let subject = "";
    let body = cleanText;

    // More robust regex for "Subject:" (case insensitive, optional space/line)
    const subjectMatch = cleanText.match(/^Subject\s*(?:line)?\s*:\s*(.+)$/mi);
    if (subjectMatch) {
      subject = subjectMatch[1].trim();
      body = cleanText.replace(subjectMatch[0], "").trim();
    }

    if (!subject || subject.length < 3) {
      subject = "Regarding your request";
    }

    body = body.replace(/\n{3,}/g, "\n\n").trim();
    return { subject, body };
  };

  const openInGmail = (to: string, subject: string, body: string) => {
    const encodedSubject = encodeURIComponent(subject);
    const encodedBody = encodeURIComponent(body);
    const encodedTo = encodeURIComponent(to);

    const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

    if (isMobile) {
      window.location.href = `mailto:${encodedTo}?subject=${encodedSubject}&body=${encodedBody}`;
    } else {
      const gmailUrl =
        "https://mail.google.com/mail/?view=cm&fs=1" +
        `&to=${encodedTo}` +
        `&su=${encodedSubject}` +
        `&body=${encodedBody}`;

      window.open(gmailUrl, "_blank");
    }
  };

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <main className="min-h-screen bg-[#05070a] text-zinc-100 selection:bg-indigo-500/30 font-sans">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(79,70,229,0.15),transparent_50%)] pointer-events-none" />

      {/* Toast Notification */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className={`fixed top-6 left-1/2 -translate-x-1/2 z-[100] px-4 py-2 rounded-full border shadow-2xl backdrop-blur-md flex items-center gap-2 ${toast.type === "success"
              ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
              : "bg-red-500/10 border-red-500/20 text-red-400"
              }`}
          >
            {toast.type === "success" ? <Check className="w-4 h-4" /> : <Trash2 className="w-4 h-4" />}
            <span className="text-sm font-medium">{toast.message}</span>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="max-w-6xl mx-auto px-6 py-12 md:py-24 relative z-10">

        {/* Header */}
        <motion.header
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="text-center mb-16 space-y-4"
        >
          <motion.div
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold tracking-wider uppercase mb-2"
            variants={itemVariants}
          >
            <Sparkles className="w-3.5 h-3.5" />
            AI-Powered Communications
          </motion.div>
          <motion.h1
            className="text-5xl md:text-7xl font-bold tracking-tight text-white"
            variants={itemVariants}
          >
            Generate <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400 text-glow">Magic</span> Emails
          </motion.h1>
          <motion.p
            className="text-lg text-zinc-400 max-w-2xl mx-auto"
            variants={itemVariants}
          >
            Transform your thoughts into professional, polished correspondence in seconds.
            Choose your tone, select a template, and let AI do the heavy lifting.
          </motion.p>
        </motion.header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

          {/* Main Input Card */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="lg:col-span-7 space-y-6"
          >
            <section className="bg-zinc-900/50 backdrop-blur-xl border border-white/10 rounded-3xl p-6 md:p-8 shadow-2xl relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 blur-[100px] pointer-events-none group-hover:bg-indigo-500/10 transition-colors" />

              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-zinc-400 ml-1 flex items-center gap-2">
                      <MessageSquare className="w-4 h-4" /> Tone
                    </label>
                    <div className="relative">
                      <select
                        value={tone}
                        onChange={(e) => setTone(e.target.value)}
                        className="w-full h-12 rounded-xl bg-white/5 border border-white/10 px-4 py-2 text-zinc-100 appearance-none focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all cursor-pointer"
                      >
                        {TONES.map(t => <option key={t} value={t} className="bg-zinc-900">{t}</option>)}
                      </select>
                      <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 pointer-events-none" />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-zinc-400 ml-1 flex items-center gap-2">
                      <Layout className="w-4 h-4" /> Template
                    </label>
                    <div className="relative">
                      <select
                        value={template}
                        onChange={(e) => setTemplate(e.target.value)}
                        className="w-full h-12 rounded-xl bg-white/5 border border-white/10 px-4 py-2 text-zinc-100 appearance-none focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all cursor-pointer"
                      >
                        {TEMPLATES.map(t => <option key={t} value={t} className="bg-zinc-900">{t}</option>)}
                      </select>
                      <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 pointer-events-none" />
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-zinc-400 ml-1">Email Purpose</label>
                  <input
                    className="w-full h-12 rounded-xl bg-white/5 border border-white/10 px-4 py-2 text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all font-medium"
                    placeholder="e.g., Asking for sick leave, Applying for internship"
                    value={context}
                    onChange={(e) => setContext(e.target.value)}
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-zinc-400 ml-1">Dates / Deadlines</label>
                    <input
                      className="w-full h-12 rounded-xl bg-white/5 border border-white/10 px-4 py-2 text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                      placeholder="e.g., Oct 24th to 26th"
                      value={dates}
                      onChange={(e) => setDates(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-zinc-400 ml-1">Your Name</label>
                    <input
                      className="w-full h-12 rounded-xl bg-white/5 border border-white/10 px-4 py-2 text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                      placeholder="e.g., Alex Johnson"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-zinc-400 ml-1">Key Details (Optional)</label>
                  <textarea
                    rows={4}
                    className="w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all resize-none"
                    placeholder="Provide context, specific points to mention, or constraints..."
                    value={keyPoints}
                    onChange={(e) => setKeyPoints(e.target.value)}
                  />
                </div>

                <motion.button
                  whileHover={{ scale: 1.01, backgroundColor: "rgba(255, 255, 255, 0.95)" }}
                  whileTap={{ scale: 0.99 }}
                  onClick={generateEmail}
                  disabled={loading}
                  className="w-full h-13 rounded-xl bg-white text-[#05070a] py-3 font-bold text-lg shadow-[0_0_20px_rgba(255,255,255,0.15)] disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <div className="w-5 h-5 border-3 border-current border-t-transparent rounded-full animate-spin" />
                      Crafting your email...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      Generate Email
                    </>
                  )}
                </motion.button>
              </div>
            </section>
          </motion.div>

          {/* Right Column: Preview / History */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-5 space-y-6"
          >
            <div className="flex items-center gap-2 mb-2 px-1">
              <button
                onClick={() => setShowHistory(false)}
                className={`text-sm font-semibold px-4 py-2 rounded-full transition-all ${!showHistory ? "bg-white/10 text-white border border-white/10" : "text-zinc-500 hover:text-zinc-300"
                  }`}
              >
                Preview
              </button>
              <button
                onClick={() => setShowHistory(true)}
                className={`text-sm font-semibold px-4 py-2 rounded-full transition-all flex items-center gap-2 ${showHistory ? "bg-white/10 text-white border border-white/10" : "text-zinc-500 hover:text-zinc-300"
                  }`}
              >
                History {history.length > 0 && <span className="w-5 h-5 bg-indigo-500 rounded-full text-[10px] flex items-center justify-center text-white">{history.length}</span>}
              </button>
            </div>

            <AnimatePresence mode="wait">
              {showHistory ? (
                <motion.section
                  key="history"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="bg-zinc-900/40 border border-white/10 rounded-3xl p-6 h-[600px] flex flex-col"
                >
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-lg font-bold flex items-center gap-2">
                      <History className="w-5 h-5 text-indigo-400" /> Recent Drafts
                    </h2>
                    {history.length > 0 && (
                      <button onClick={clearHistory} className="text-xs text-zinc-500 hover:text-red-400 transition-colors flex items-center gap-1">
                        <Trash2 className="w-3 h-3" /> Clear All
                      </button>
                    )}
                  </div>

                  <div className="flex-1 overflow-y-auto space-y-4 pr-2 scrollbar-thin scrollbar-thumb-white/10">
                    {history.length === 0 ? (
                      <div className="h-full flex flex-col items-center justify-center text-zinc-600 gap-3">
                        <History className="w-12 h-12 opacity-20" />
                        <p className="text-sm">No history yet</p>
                      </div>
                    ) : (
                      history.map((item) => (
                        <motion.div
                          key={item.id}
                          layout
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          className="p-4 rounded-2xl bg-white/5 border border-white/5 hover:border-white/10 transition-all group cursor-pointer"
                          onClick={() => {
                            setPreview(item.body);
                            setEditableDraft(item.body);
                            setShowHistory(false);
                          }}
                        >
                          <div className="flex justify-between items-start mb-1">
                            <span className="text-xs text-indigo-400 font-medium uppercase tracking-wider">
                              {new Date(item.timestamp).toLocaleDateString()}
                            </span>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                deleteHistoryItem(item.id);
                              }}
                              className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500/10 rounded-md text-red-500 transition-all"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                          <h3 className="text-sm font-bold text-zinc-200 line-clamp-1 mb-1">{item.subject}</h3>
                          <p className="text-xs text-zinc-500 line-clamp-2 italic">"{item.context}"</p>
                        </motion.div>
                      ))
                    )}
                  </div>
                </motion.section>
              ) : (
                <motion.section
                  key="preview"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="space-y-4"
                >
                  <div className="bg-zinc-900/40 border border-white/10 rounded-3xl p-1 shadow-2xl overflow-hidden min-h-[600px] flex flex-col">
                    {preview ? (
                      <>
                        <div className="p-4 border-b border-white/5 flex items-center justify-between bg-white/5">
                          <h3 className="text-sm font-bold text-zinc-400 flex items-center gap-2">
                            <Mail className="w-4 h-4" /> Draft Preview
                          </h3>
                          <div className="flex gap-1 items-center">
                            <button
                              onClick={() => {
                                navigator.clipboard.writeText(editableDraft);
                                setCopied(true);
                                showToast("Copied to clipboard!");
                                setTimeout(() => setCopied(false), 2000);
                              }}
                              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 transition-all"
                              title="Copy to clipboard"
                            >
                              {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4 text-zinc-400" />}
                            </button>
                            <button
                              onClick={() => {
                                setContext("");
                                setDates("");
                                setKeyPoints("");
                                setPreview("");
                                setEditableDraft("");
                              }}
                              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 transition-all"
                              title="Clear"
                            >
                              <RotateCcw className="w-4 h-4 text-zinc-400" />
                            </button>
                          </div>
                        </div>

                        <div className="flex-1 p-4 overflow-y-auto space-y-4">
                          <div className="space-y-2">
                            <label className="text-[10px] font-bold uppercase tracking-widest text-zinc-600">Recipient Email (REQUIRED for Gmail)</label>
                            <input
                              className={`w-full h-10 rounded-xl bg-white/5 border px-4 text-sm focus:outline-none transition-all ${toEmail && !isValidEmail(toEmail)
                                ? "border-amber-500/40 focus:ring-amber-500/20 shadow-[0_0_10px_rgba(245,158,11,0.1)]"
                                : "border-white/10 focus:ring-indigo-500/20"
                                }`}
                              placeholder="example@gmail.com"
                              value={toEmail}
                              onChange={(e) => setToEmail(e.target.value)}
                            />
                            {!isValidEmail(toEmail) && toEmail.length > 0 && (
                              <p className="text-[10px] text-amber-500 font-medium ml-1">Please enter a valid email to enable Gmail option</p>
                            )}
                          </div>

                          <div className="space-y-2 flex flex-col flex-1">
                            <label className="text-[10px] font-bold uppercase tracking-widest text-zinc-600">Editable Content</label>
                            <textarea
                              className="flex-1 w-full min-h-[350px] rounded-2xl bg-white/5 border border-white/10 px-4 py-4 text-sm text-zinc-300 focus:outline-none focus:ring-1 focus:ring-indigo-500/30 transition-all font-mono leading-relaxed"
                              value={editableDraft}
                              onChange={(e) => setEditableDraft(e.target.value)}
                            />
                          </div>
                        </div>

                        <div className="p-4 bg-zinc-950/50 border-t border-white/10 flex gap-3">
                          <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            disabled={!isValidEmail(toEmail) || !editableDraft || editableDraft.includes("Error generating email")}
                            onClick={() => {
                              const { subject, body } = extractSubjectAndBody(editableDraft);
                              openInGmail(toEmail, subject, body);
                            }}
                            className={`flex-1 h-12 rounded-xl font-bold flex items-center justify-center gap-2 transition-all ${isValidEmail(toEmail) && editableDraft && !editableDraft.includes("Error generating email")
                              ? "bg-indigo-600 text-white shadow-lg shadow-indigo-500/20 hover:bg-indigo-500 animate-pulse-slow"
                              : "bg-white/5 text-zinc-600 cursor-not-allowed border border-white/5"
                              }`}
                          >
                            <Mail className="w-5 h-5" /> Open in Gmail
                          </motion.button>
                        </div>
                      </>
                    ) : (
                      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center space-y-6">
                        <div className="w-20 h-20 rounded-full bg-indigo-500/5 flex items-center justify-center">
                          <Mail className="w-10 h-10 text-indigo-500/30" />
                        </div>
                        <div className="max-w-[240px]">
                          <h3 className="text-zinc-300 font-bold mb-2">No Preview Available</h3>
                          <p className="text-sm text-zinc-600">Your generated email will appear here. Fill out the form to get started.</p>
                        </div>
                      </div>
                    )}
                  </div>
                </motion.section>
              )}
            </AnimatePresence>
          </motion.div>
        </div>

        {/* Features Section */}
        <section className="mt-40 grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              icon: <MessageSquare className="w-6 h-6 text-indigo-400" />,
              title: "Multiple Tones",
              desc: "From formal business reports to casual catch-ups, we've got you covered."
            },
            {
              icon: <Layout className="w-6 h-6 text-cyan-400" />,
              title: "Smart Templates",
              desc: "Pro-structured templates for any common scenario you face daily."
            },
            {
              icon: <History className="w-6 h-6 text-emerald-400" />,
              title: "Draft History",
              desc: "Never lose a good draft again. We save your last 10 emails locally."
            }
          ].map((feature, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="p-8 rounded-3xl bg-zinc-900/30 border border-white/5 hover:border-white/10 transition-all hover:bg-zinc-900/50 group"
            >
              <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
              <p className="text-zinc-500 leading-relaxed text-sm">{feature.desc}</p>
            </motion.div>
          ))}
        </section>

        {/* Footer */}
        <footer className="mt-40 pt-12 border-t border-white/5 text-center space-y-4">
          <p className="text-zinc-600 text-sm">© 2026 AI Email Generator. Built for the future of communication.</p>
          <div className="flex justify-center gap-6">
            <a href="#" className="text-zinc-500 hover:text-white transition-colors"><ExternalLink className="w-4 h-4" /></a>
          </div>
        </footer>
      </div>

      <style jsx global>{`
        .text-glow {
          text-shadow: 0 0 30px rgba(99, 102, 241, 0.5);
        }
        
        .scrollbar-thin::-webkit-scrollbar {
          width: 4px;
        }
        
        .scrollbar-thin::-webkit-scrollbar-track {
          background: transparent;
        }
        
        .scrollbar-thin::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 20px;
        }
      `}</style>
    </main>
  );
}
