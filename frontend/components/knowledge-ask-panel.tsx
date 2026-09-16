"use client";

import { useState } from "react";
import { askKnowledgeBase, type RAGAnswer } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Field } from "@/components/ui/field";
import { Button } from "@/components/ui/button";
import { MarkdownText } from "@/components/markdown-text";

export function KnowledgeAskPanel() {
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [answer, setAnswer] = useState<RAGAnswer | null>(null);

  async function handleAsk(e: React.FormEvent) {
    e.preventDefault();
    const token = getToken();
    if (!token || !question.trim()) return;

    setAsking(true);
    setError(null);
    setAnswer(null);

    try {
      const response = await askKnowledgeBase(token, question);
      setAnswer(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't get an answer.");
    } finally {
      setAsking(false);
    }
  }

  return (
    <div className="rounded-2xl border border-line bg-white p-6">
      <h2 className="text-lg text-navy">Ask CareerIQ</h2>
      <p className="mt-1 text-sm text-ink/60">
        Ask a technical question — answers are grounded in a small curated
        knowledge base, not general model knowledge.
      </p>

      <form onSubmit={handleAsk} className="mt-4 flex flex-col gap-3">
        <Field
          label="Your question"
          name="question"
          placeholder="e.g. Why does chunking matter for RAG?"
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
          <MarkdownText content={answer.answer} />

          {answer.grounded && answer.sources.length > 0 && (
            <div className="mt-4">
              <p className="text-xs font-medium text-ink/50">Sources</p>
              <ul className="mt-2 space-y-1">
                {answer.sources.map((s, i) => (
                  <li key={i} className="text-xs text-ink/60">
                    <span className="font-medium text-ink/80">{s.topic}</span>{" "}
                    · {s.title} · similarity {s.similarity.toFixed(2)}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}