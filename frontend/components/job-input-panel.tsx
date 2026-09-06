"use client";

import { useEffect, useState } from "react";
import {
  listJobs,
  createJob,
  parseJob,
  type JobRead,
  type JobProfileData,
} from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Field } from "@/components/ui/field";
import { Button } from "@/components/ui/button";
import { JobProfileCard } from "@/components/job-profile-card";

const MIN_LENGTH = 50;

export function JobInputPanel({
  compact = false,
}: {
  /** Smaller heading, fewer rows, and no history — used when embedded on the dashboard overview. */
  compact?: boolean;
}) {
  const [title, setTitle] = useState("");
  const [company, setCompany] = useState("");
  const [rawText, setRawText] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [job, setJob] = useState<JobRead | null>(null);
  const [history, setHistory] = useState<JobRead[]>([]);
  const [parsing, setParsing] = useState(false);
  const [parseError, setParseError] = useState<string | null>(null);
  const [profile, setProfile] = useState<JobProfileData | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) return;
    listJobs(token)
      .then(setHistory)
      .catch(() => {
        // Non-critical — the form still works without history.
      });
  }, []);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    const token = getToken();
    if (!token) return;

    if (rawText.trim().length < MIN_LENGTH) {
      setError(
        `Paste the full job description — at least ${MIN_LENGTH} characters.`
      );
      return;
    }

    setSaving(true);
    setError(null);
    setProfile(null);
    setParseError(null);

    try {
      const response = await createJob(token, {
        title: title || undefined,
        company: company || undefined,
        raw_text: rawText,
      });
      setJob(response);
      setHistory((prev) => [response, ...prev]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't save this job.");
    } finally {
      setSaving(false);
    }
  }

  async function handleParse() {
    const token = getToken();
    if (!job || !token) return;

    setParsing(true);
    setParseError(null);

    try {
      const response = await parseJob(token, job.id);
      if (response.status === "ready" && response.data) {
        setProfile(response.data);
      } else {
        setParseError(
          response.error_message ?? "Couldn't extract requirements from this posting."
        );
      }
    } catch (err) {
      setParseError(err instanceof Error ? err.message : "Extraction failed.");
    } finally {
      setParsing(false);
    }
  }

  const Heading = compact ? "h2" : "h1";

  return (
    <div>
      <Heading className={compact ? "text-lg text-navy" : "text-2xl text-navy"}>
        Job description
      </Heading>
      <p className="mt-2 text-sm text-ink/60">
        Paste a job description to pull out its requirements — this is what
        your resume will eventually be matched against.
      </p>

      <form
        onSubmit={handleSave}
        className="mt-4 flex flex-col gap-4 rounded-2xl border border-line bg-white p-6"
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <Field
            label="Job title (optional)"
            name="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <Field
            label="Company (optional)"
            name="company"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label htmlFor="raw_text" className="text-sm font-medium text-ink">
            Job description
          </label>
          <textarea
            id="raw_text"
            rows={compact ? 6 : 10}
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
            placeholder="Paste the full job posting here…"
            className="rounded-lg border border-line bg-white px-3 py-2 text-sm text-ink placeholder:text-ink/40 focus:border-navy"
          />
        </div>

        {error && <p className="text-sm text-gap">{error}</p>}

        <Button type="submit" disabled={saving} className="mt-2 sm:w-auto">
          {saving ? "Saving…" : "Save job description"}
        </Button>
      </form>

      {job && (
        <div className="mt-6 rounded-2xl border border-match/30 bg-match-soft p-6">
          <p className="text-sm font-medium text-match">Job saved</p>
          <p className="mt-1 text-sm text-ink/70">
            {job.title ?? "Untitled role"}
            {job.company ? ` at ${job.company}` : ""}
          </p>
          <Button
            type="button"
            variant="ghost"
            onClick={handleParse}
            disabled={parsing}
            className="mt-4 w-auto px-0 text-navy hover:underline"
          >
            {parsing ? "Extracting…" : "Extract requirements →"}
          </Button>
        </div>
      )}

      {parseError && <p className="mt-4 text-sm text-gap">{parseError}</p>}

      {profile && <JobProfileCard data={profile} />}

      {!compact && history.length > 0 && (
        <div className="mt-8">
          <h2 className="text-sm font-medium text-ink/70">Previously saved</h2>
          <ul className="mt-3 space-y-2">
            {history.map((j) => (
              <li
                key={j.id}
                className="rounded-lg border border-line bg-white px-4 py-3 text-sm text-ink/80"
              >
                {j.title ?? "Untitled role"}
                {j.company ? ` · ${j.company}` : ""}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}