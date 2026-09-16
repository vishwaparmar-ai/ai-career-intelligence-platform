"use client";

import { useState } from "react";
import {
  startInterviewSession,
  submitInterviewAnswer,
  type InterviewSessionRead,
} from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Button } from "@/components/ui/button";

export function InterviewPanel({
  resumeId,
  jobId,
}: {
  resumeId?: string;
  jobId?: string;
}) {
  const [session, setSession] = useState<InterviewSessionRead | null>(null);
  const [answerText, setAnswerText] = useState("");
  const [starting, setStarting] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleStart() {
    const token = getToken();
    if (!token || !resumeId || !jobId) return;

    setStarting(true);
    setError(null);

    try {
      const newSession = await startInterviewSession(token, resumeId, jobId);
      setSession(newSession);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Couldn't start an interview session."
      );
    } finally {
      setStarting(false);
    }
  }

  async function handleSubmitAnswer(e: React.FormEvent) {
    e.preventDefault();
    const token = getToken();
    if (!token || !session || !answerText.trim()) return;

    setSubmitting(true);
    setError(null);

    try {
      const updated = await submitInterviewAnswer(
        token,
        session.id,
        answerText.trim()
      );
      setSession(updated);
      setAnswerText("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't submit that answer.");
    } finally {
      setSubmitting(false);
    }
  }

  // Not started yet.
  if (!session) {
    return (
      <div className="rounded-2xl border border-line bg-white p-6 text-center">
        <h2 className="text-lg text-navy">Interview practice</h2>
        <p className="mx-auto mt-1 max-w-sm text-sm text-ink/60">
          Get interview questions built from this exact job and your
          resume — including a couple that probe your actual gap areas.
        </p>
        {error && <p className="mt-3 text-sm text-gap">{error}</p>}
        <Button
          type="button"
          onClick={handleStart}
          disabled={starting}
          className="mt-4 w-auto px-6"
        >
          {starting ? "Preparing questions…" : "Start interview practice"}
        </Button>
      </div>
    );
  }

  const isComplete = session.status === "completed";
  const currentQuestion = session.questions[session.current_index];

  return (
    <div className="rounded-2xl border border-line bg-white p-6">
      <div className="flex items-baseline justify-between">
        <h2 className="text-lg text-navy">Interview practice</h2>
        <span className="text-xs text-ink/40">
          {isComplete
            ? `${session.questions.length} of ${session.questions.length} answered`
            : `Question ${session.current_index + 1} of ${session.questions.length}`}
        </span>
      </div>

      {!isComplete && currentQuestion && (
        <div className="mt-4">
          <p className="text-sm text-ink">{currentQuestion.question}</p>
          {currentQuestion.focus_skill && (
            <p className="mt-1 text-xs text-ink/40">
              Focus: {currentQuestion.focus_skill}
            </p>
          )}

          <form onSubmit={handleSubmitAnswer} className="mt-4 flex flex-col gap-3">
            <textarea
              rows={5}
              value={answerText}
              onChange={(e) => setAnswerText(e.target.value)}
              placeholder="Type your answer…"
              className="rounded-lg border border-line bg-white px-3 py-2 text-sm text-ink placeholder:text-ink/40 focus:border-navy"
            />
            {error && <p className="text-sm text-gap">{error}</p>}
            <Button
              type="submit"
              disabled={!answerText.trim() || submitting}
              className="sm:w-auto"
            >
              {submitting ? "Submitting…" : "Submit answer"}
            </Button>
          </form>
        </div>
      )}

      {isComplete && (
        <div className="mt-4">
          <p className="text-sm font-medium text-match">
            Interview complete — nice work.
          </p>
          <p className="mt-1 text-xs text-ink/50">
            Feedback and scoring on your answers is coming in a later
            update. For now, here's your transcript.
          </p>

          <ol className="mt-4 space-y-4">
            {session.questions.map((q, i) => (
              <li key={i} className="rounded-lg border border-line p-4">
                <p className="text-sm font-medium text-ink">
                  {i + 1}. {q.question}
                </p>
                <p className="mt-2 text-sm text-ink/70">
                  {q.answer || "(no answer recorded)"}
                </p>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}