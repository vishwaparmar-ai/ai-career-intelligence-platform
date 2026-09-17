"use client";

import { useState } from "react";
import {
  startInterviewSession,
  submitInterviewAnswer,
  generateInterviewFeedback,
  type InterviewSessionRead,
} from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Button } from "@/components/ui/button";

const RATING_STYLES: Record<string, string> = {
  strong: "bg-match-soft text-match",
  adequate: "bg-signal-soft text-signal",
  weak: "bg-gap-soft text-gap",
};

function RatingBadge({ label, value }: { label: string; value: string | null }) {
  const style = value ? RATING_STYLES[value.toLowerCase()] ?? "bg-navy/5 text-navy" : "bg-navy/5 text-navy";
  return (
    <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${style}`}>
      {label}: {value ?? "Not assessed"}
    </span>
  );
}

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
  const [gettingFeedback, setGettingFeedback] = useState(false);
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

  async function handleGetFeedback() {
    const token = getToken();
    if (!token || !session) return;

    setGettingFeedback(true);
    setError(null);

    try {
      const updated = await generateInterviewFeedback(token, session.id);
      setSession(updated);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Couldn't generate feedback."
      );
    } finally {
      setGettingFeedback(false);
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
  const hasFeedback = session.questions.some((q) => q.evaluation);

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
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-match">
              Interview complete — nice work.
            </p>
            {!hasFeedback && (
              <Button
                type="button"
                variant="ghost"
                onClick={handleGetFeedback}
                disabled={gettingFeedback}
                className="w-auto px-0 text-navy hover:underline"
              >
                {gettingFeedback ? "Evaluating…" : "Get feedback →"}
              </Button>
            )}
          </div>

          {error && <p className="mt-2 text-sm text-gap">{error}</p>}

          <ol className="mt-4 space-y-4">
            {session.questions.map((q, i) => (
              <li key={i} className="rounded-lg border border-line p-4">
                <p className="text-sm font-medium text-ink">
                  {i + 1}. {q.question}
                </p>
                <p className="mt-2 text-sm text-ink/70">
                  {q.answer || "(no answer recorded)"}
                </p>

                {q.evaluation && (
                  <div className="mt-4 border-t border-line pt-4">
                    <div className="flex flex-wrap gap-2">
                      <RatingBadge label="Accuracy" value={q.evaluation.technical_accuracy} />
                      <RatingBadge label="Depth" value={q.evaluation.depth} />
                      <RatingBadge label="Relevance" value={q.evaluation.relevance} />
                    </div>

                    {q.evaluation.strengths.length > 0 && (
                      <div className="mt-3">
                        <p className="text-xs font-medium text-ink/60">Strengths</p>
                        <ul className="mt-1 list-disc space-y-0.5 pl-5 text-sm text-ink/70">
                          {q.evaluation.strengths.map((s, j) => (
                            <li key={j}>{s}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {q.evaluation.missing_concepts.length > 0 && (
                      <div className="mt-3">
                        <p className="text-xs font-medium text-ink/60">
                          Missing concepts
                        </p>
                        <ul className="mt-1 list-disc space-y-0.5 pl-5 text-sm text-ink/70">
                          {q.evaluation.missing_concepts.map((s, j) => (
                            <li key={j}>{s}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {q.evaluation.improvement_advice && (
                      <p className="mt-3 rounded-lg bg-navy/5 p-3 text-sm text-ink/80">
                        <span className="font-medium text-ink">To improve:</span>{" "}
                        {q.evaluation.improvement_advice}
                      </p>
                    )}
                  </div>
                )}
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}