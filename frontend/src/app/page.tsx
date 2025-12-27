"use client";

import { useState, useMemo } from "react";
import ReactMarkdown from "react-markdown";
import { motion, useReducedMotion, easeOut } from "framer-motion";
import { SplineSceneBasic } from "@/components/ui/demo";

export default function Home() {
  const prefersReducedMotion = useReducedMotion();

  const fadeUp = {
    hidden: { opacity: 0, y: prefersReducedMotion ? 0 : 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: prefersReducedMotion ? 0 : 0.6,
        ease: easeOut,
      },
    },
  };

  const [context, setContext] = useState("");
  const [dates, setDates] = useState("");
  const [keyPoints, setKeyPoints] = useState("");
  const [name, setName] = useState("");
  const [toEmail, setToEmail] = useState("");

  const [preview, setPreview] = useState("");
  const [editableDraft, setEditableDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const isValidEmail = (email: string) =>
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  const generateEmail = async () => {
    setLoading(true);
    setCopied(false);

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/generate`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            context,
            dates,
            key_points: keyPoints,
            name,
          }),
        }
      );

      const data = await res.json();
      setPreview(data.email);
      setEditableDraft(data.email);
    } catch {
      console.error("Generation failed");
    } finally {
      setLoading(false);
    }
  };

  const extractSubjectAndBody = (text: string) => {
    let subject = "";
    let body = text.trim();

    const subjectMatch = text.match(/^\s*subject\s*:\s*(.+)$/im);
    if (subjectMatch) {
      subject = subjectMatch[1].trim();
      body = text.replace(subjectMatch[0], "").trim();
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

    const isMobile =
      /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

    if (isMobile) {
      window.location.href =
        `mailto:${encodedTo}?subject=${encodedSubject}&body=${encodedBody}`;
    } else {
      const gmailUrl =
        "https://mail.google.com/mail/?view=cm&fs=1" +
        `&to=${encodedTo}` +
        `&su=${encodedSubject}` +
        `&body=${encodedBody}`;

      window.open(gmailUrl, "_blank");
    }
  };

  const renderedMarkdown = useMemo(
    () => <ReactMarkdown>{editableDraft}</ReactMarkdown>,
    [editableDraft]
  );

  return (
    <main className="min-h-screen bg-[#0a0d14] text-white">
      <div className="max-w-6xl mx-auto px-6 py-20 space-y-20">

        <motion.header
          variants={fadeUp}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="text-center max-w-2xl mx-auto"
        >
          <h1 className="text-4xl font-medium">AI Email Generator</h1>
          <p className="mt-3 text-zinc-400">
            Write professional emails with AI.
          </p>
        </motion.header>

        <motion.section
          variants={fadeUp}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="relative rounded-3xl overflow-hidden border border-white/10"
        >
          <div className="absolute inset-0 bg-white/5 backdrop-blur-xl" />

          <div className="relative grid grid-cols-1 lg:grid-cols-2 min-h-[440px]">

            <div className="p-8 space-y-4">
              <input className="w-full rounded-xl bg-white/10 border border-white/15 px-4 py-3"
                placeholder="What is the email about?"
                value={context}
                onChange={(e) => setContext(e.target.value)}
              />

              <input className="w-full rounded-xl bg-white/10 border border-white/15 px-4 py-3"
                placeholder="Relevant dates"
                value={dates}
                onChange={(e) => setDates(e.target.value)}
              />

              <textarea rows={3}
                className="w-full rounded-xl bg-white/10 border border-white/15 px-4 py-3"
                placeholder="Key points"
                value={keyPoints}
                onChange={(e) => setKeyPoints(e.target.value)}
              />

              <input className="w-full rounded-xl bg-white/10 border border-white/15 px-4 py-3"
                placeholder="Your name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />

              <input
                className={`w-full rounded-xl bg-white/10 border px-4 py-3 ${
                  toEmail && !isValidEmail(toEmail)
                    ? "border-yellow-400/40"
                    : "border-white/15"
                }`}
                placeholder="Recipient email (required for Gmail)"
                value={toEmail}
                onChange={(e) => setToEmail(e.target.value)}
              />

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={generateEmail}
                disabled={loading}
                className="w-full rounded-xl bg-white text-black py-3 font-medium"
              >
                {loading ? "Generating..." : "Generate Email"}
              </motion.button>
            </div>

            <motion.div
              initial={{ opacity: 0, x: 40 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, ease: easeOut }}
              className="relative hidden lg:block"
            >
              <SplineSceneBasic />
            </motion.div>
          </div>
        </motion.section>

        {preview && (
          <motion.section
            variants={fadeUp}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="rounded-3xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 space-y-4"
          >
            <div className="flex justify-between items-center gap-2 flex-nowrap">
              <h2 className="text-lg font-medium whitespace-nowrap">
                Email Draft
              </h2>

              <div className="flex items-center gap-2 flex-nowrap">
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(editableDraft);
                    setCopied(true);
                    setTimeout(() => setCopied(false), 1200);
                  }}
                  className="px-3 py-1.5 text-sm rounded-md bg-white/10 hover:bg-white/20 whitespace-nowrap"
                >
                  {copied ? "Copied" : "Copy"}
                </button>

                <button
                  onClick={generateEmail}
                  className="px-3 py-1.5 text-sm rounded-md bg-white/10 hover:bg-white/20 whitespace-nowrap"
                >
                  Regenerate
                </button>

                <button
                  disabled={!isValidEmail(toEmail)}
                  onClick={() => {
                    const { subject, body } =
                      extractSubjectAndBody(editableDraft);
                    openInGmail(toEmail, subject, body);
                  }}
                  className={`px-3 py-1.5 text-sm rounded-md font-medium whitespace-nowrap transition ${
                    isValidEmail(toEmail)
                      ? "bg-white text-black hover:bg-zinc-200"
                      : "bg-white/10 text-zinc-400 cursor-not-allowed"
                  }`}
                >
                  Open in Gmail
                </button>
              </div>
            </div>

            <textarea
              className="w-full min-h-[200px] rounded-xl bg-white/10 border border-white/15 px-4 py-3"
              value={editableDraft}
              onChange={(e) => setEditableDraft(e.target.value)}
            />

            <div className="prose prose-invert max-w-none border-t border-white/10 pt-4">
              {renderedMarkdown}
            </div>
          </motion.section>
        )}
      </div>
    </main>
  );
}
