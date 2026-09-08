"use client";

import { useEffect, useState } from "react";
import {
  listResumes,
  listJobs,
  runAnalysis,
  type ResumeRead,
  type JobRead,
  type MatchResult,
  type GapAnalysis,
} from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { MatchResultCard } from "@/components/match-result-card";
import { GapAnalysisCard } from "@/components/gap-analysis-card";

export function AnalysisPanel() {
  const [resumes, setResumes] = useState<ResumeRead[]>([]);
  const [jobs, setJobs] = useState<JobRead[]>([]);
  const [resumeId, setResumeId] = useState("");
  const [jobId, setJobId] = useState("");
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<MatchResult | null>(null);
  const [gapAnalysis, setGapAnalysis] = useState<GapAnalysis | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) return;
    listResumes(token).then((rs) => {
      setResumes(rs.filter((r) => r.status === "ready"));
    });
    listJobs(token).then(setJobs);
  }, []);

  async function handleRun() {
    const token = getToken();
    if (!token || !resumeId || !jobId) return;

    setRunning(true);
    setError(null);
    setResult(null);
    setGapAnalysis(null);

    try {
      const analysis = await runAnalysis(token, resumeId, jobId);
      setResult(analysis.result);
      setGapAnalysis(analysis.gap_analysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't run this analysis.");
    } finally {
      setRunning(false);
    }
  }

  if (resumes.length === 0 || jobs.length === 0) {
    return (
      <section className="rounded-2xl border border-line bg-white p-6">
        <h2 className="text-sm font-medium text-ink/70">Readiness score</h2>
        <p className="mt-4 text-sm text-ink/50">
          Upload a resume and save a job description above, then come back
          here to see your score.
        </p>
      </section>
    );
  }

  return (
    <div>
      <div className="rounded-2xl border border-line bg-white p-6">
        <h2 className="text-lg text-navy">Run a readiness check</h2>
        <p className="mt-1 text-sm text-ink/60">
          Pick a resume and a job you&apos;ve already extracted a profile
          for.
        </p>

        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-ink">Resume</label>
            <select
              value={resumeId}
              onChange={(e) => setResumeId(e.target.value)}
              className="rounded-lg border border-line bg-white px-3 py-2 text-sm text-ink"
            >
              <option value="">Select a resume…</option>
              {resumes.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.original_filename}
                </option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-ink">Job</label>
            <select
              value={jobId}
              onChange={(e) => setJobId(e.target.value)}
              className="rounded-lg border border-line bg-white px-3 py-2 text-sm text-ink"
            >
              <option value="">Select a job…</option>
              {jobs.map((j) => (
                <option key={j.id} value={j.id}>
                  {j.title ?? "Untitled role"}
                  {j.company ? ` · ${j.company}` : ""}
                </option>
              ))}
            </select>
          </div>
        </div>

        {error && <p className="mt-4 text-sm text-gap">{error}</p>}

        <Button
          type="button"
          onClick={handleRun}
          disabled={!resumeId || !jobId || running}
          className="mt-4 sm:w-auto"
        >
          {running ? "Scoring…" : "Get readiness score"}
        </Button>
      </div>

      {result && (
        <div className="mt-6">
          <MatchResultCard result={result} />
        </div>
      )}

      {gapAnalysis && (
        <div className="mt-6">
          <GapAnalysisCard gapAnalysis={gapAnalysis} />
        </div>
      )}
    </div>
  );
}