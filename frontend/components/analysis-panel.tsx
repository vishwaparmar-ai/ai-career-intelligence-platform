"use client";

import { useEffect, useState } from "react";
import {
  listResumes,
  listJobs,
  runAnalysis,
  generateRoadmap,
  type ResumeRead,
  type JobRead,
  type MatchResult,
  type GapAnalysis,
  type RoadmapData,
} from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { MatchResultCard } from "@/components/match-result-card";
import { GapAnalysisCard } from "@/components/gap-analysis-card";
import { RoadmapCard } from "@/components/roadmap-card";

type RoadmapChoice = "unanswered" | "generating" | "shown" | "declined";

export function AnalysisPanel() {
  const [resumes, setResumes] = useState<ResumeRead[]>([]);
  const [jobs, setJobs] = useState<JobRead[]>([]);
  const [resumeId, setResumeId] = useState("");
  const [jobId, setJobId] = useState("");
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [result, setResult] = useState<MatchResult | null>(null);
  const [gapAnalysis, setGapAnalysis] = useState<GapAnalysis | null>(null);

  const [roadmapChoice, setRoadmapChoice] = useState<RoadmapChoice>("unanswered");
  const [roadmap, setRoadmap] = useState<RoadmapData | null>(null);
  const [roadmapError, setRoadmapError] = useState<string | null>(null);

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
    setAnalysisId(null);
    // A fresh analysis needs a fresh roadmap decision — don't carry over
    // a previous run's "declined" or generated roadmap onto a new one.
    setRoadmapChoice("unanswered");
    setRoadmap(null);
    setRoadmapError(null);

    try {
      const analysis = await runAnalysis(token, resumeId, jobId);
      setAnalysisId(analysis.id);
      setResult(analysis.result);
      setGapAnalysis(analysis.gap_analysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't run this analysis.");
    } finally {
      setRunning(false);
    }
  }

  async function handleGenerateRoadmap() {
    const token = getToken();
    if (!token || !analysisId) return;

    setRoadmapChoice("generating");
    setRoadmapError(null);

    try {
      const response = await generateRoadmap(token, analysisId);
      if (response.status === "ready" && response.data) {
        setRoadmap(response.data);
        setRoadmapChoice("shown");
      } else {
        setRoadmapError(
          response.error_message ?? "Couldn't generate a roadmap. Try again."
        );
        setRoadmapChoice("unanswered");
      }
    } catch (err) {
      setRoadmapError(
        err instanceof Error ? err.message : "Roadmap generation failed."
      );
      setRoadmapChoice("unanswered");
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

      {gapAnalysis && roadmapChoice === "unanswered" && (
        <div className="mt-6 rounded-2xl border border-line bg-white p-6 text-center">
          <p className="text-sm font-medium text-ink">
            Want a personalized roadmap?
          </p>
          <p className="mx-auto mt-1 max-w-sm text-sm text-ink/60">
            We&apos;ll turn the gaps above into a concrete 30-day plan —
            this makes an AI call, so it only runs if you ask for it.
          </p>
          <div className="mt-4 flex justify-center gap-3">
            <Button
              type="button"
              onClick={handleGenerateRoadmap}
              className="w-auto px-6"
            >
              Yes, generate it
            </Button>
            <Button
              type="button"
              variant="ghost"
              onClick={() => setRoadmapChoice("declined")}
              className="w-auto px-4"
            >
              Not now
            </Button>
          </div>
        </div>
      )}

      {roadmapChoice === "generating" && (
        <p className="mt-6 text-center text-sm text-ink/60">
          Building your roadmap…
        </p>
      )}

      {roadmapError && (
        <p className="mt-4 text-center text-sm text-gap">{roadmapError}</p>
      )}

      {roadmap && roadmapChoice === "shown" && (
        <div className="mt-6">
          <RoadmapCard roadmap={roadmap} />
        </div>
      )}
    </div>
  );
}