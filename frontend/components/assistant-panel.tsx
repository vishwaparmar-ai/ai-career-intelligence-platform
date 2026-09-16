"use client";

import { useState } from "react";
import { askAssistant } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Field } from "@/components/ui/field";
import { Button } from "@/components/ui/button";
import { MarkdownText } from "@/components/markdown-text";

export function AssistantPanel({
  resumeId,
  jobId,
}: {
  resumeId?: string;
  jobId?: string;
}) {
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [answer, setAnswer] = useState<string | null>(null);
  const [toolsUsed, setToolsUsed] = useState<string[]>([]);

  async function handleAsk(e: React.FormEvent) {
    e.preventDefault();
    const token = getToken();
    if (!token || !question.trim()) return;

    setAsking(true);
    setError(null);
    setAnswer(null);

    try {
      const response = await askAssistant(token, {
        question,
        resume_id: resumeId,
        job_id: jobId,
      });
      setAnswer(response.answer);
      setToolsUsed(response.tools_used);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't get an answer.");
    } finally {
      setAsking(false);
    }
  }

  return (
    <div className="rounded-2xl border border-line bg-white p-6">
      <h2 className="text-lg text-navy">Ask about this analysis</h2>
      <p className="mt-1 text-sm text-ink/60">
        Ask about the selected resume/job, or a general engineering
        concept — the assistant decides what it needs to look up.
      </p>

      <form onSubmit={handleAsk} className="mt-4 flex flex-col gap-3">
        <Field
          label="Your question"
          name="assistant_question"
          placeholder="e.g. What are my biggest skill gaps for this role?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        {error && <p className="text-sm text-gap">{error}</p>}
        <Button
          type="submit"
          disabled={!question.trim() || asking}
          className="sm:w-auto"
        >
          {asking ? "Thinking…" : "Ask"}
        </Button>
      </form>

      {answer && (
        <div className="mt-6 border-t border-line pt-6">
          <MarkdownText content={answer} />
          {toolsUsed.length > 0 && (
            <p className="mt-3 text-xs text-ink/40">
              Looked up: {toolsUsed.join(", ")}
            </p>
          )}
        </div>
      )}
    </div>
  );
}