"use client";

import { useEffect, useState } from "react";
import { listResumes, uploadResume, type ResumeRead } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Button } from "@/components/ui/button";

const MAX_SIZE_MB = 5;

export default function ResumeUploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ResumeRead | null>(null);
  const [history, setHistory] = useState<ResumeRead[]>([]);

  useEffect(() => {
    const token = getToken();
    if (!token) return;
    listResumes(token)
      .then(setHistory)
      .catch(() => {
        // Non-critical — the upload form still works without history.
      });
  }, []);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const selected = e.target.files?.[0] ?? null;
    setError(null);
    setResult(null);

    if (!selected) {
      setFile(null);
      return;
    }

    if (selected.type !== "application/pdf") {
      setError("Please choose a PDF file.");
      setFile(null);
      return;
    }

    if (selected.size > MAX_SIZE_MB * 1024 * 1024) {
      setError(`That file is too large — the limit is ${MAX_SIZE_MB}MB.`);
      setFile(null);
      return;
    }

    setFile(selected);
  }

  async function handleUpload() {
    const token = getToken();
    if (!file || !token) return;

    setUploading(true);
    setError(null);

    try {
      const response = await uploadResume(token, file);
      setResult(response);
      setHistory((prev) => [response, ...prev]);

      if (response.status === "failed") {
        setError(response.error_message ?? "Couldn't read that file.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div>
      <h1 className="text-2xl text-navy">Resume</h1>
      <p className="mt-2 text-sm text-ink/60">
        Upload a PDF resume. We&apos;ll pull out the text so it can be
        matched against a job description later.
      </p>

      <div className="mt-8 rounded-2xl border border-line bg-white p-6">
        <label
          htmlFor="resume-file"
          className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-line px-6 py-10 text-center transition-colors hover:border-navy/40"
        >
          <span className="text-sm font-medium text-ink">
            {file ? file.name : "Click to choose a PDF"}
          </span>
          <span className="text-xs text-ink/50">
            PDF only, up to {MAX_SIZE_MB}MB
          </span>
        </label>
        <input
          id="resume-file"
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={handleFileChange}
        />

        {error && <p className="mt-4 text-sm text-gap">{error}</p>}

        <Button
          type="button"
          onClick={handleUpload}
          disabled={!file || uploading}
          className="mt-6"
        >
          {uploading ? "Uploading…" : "Upload resume"}
        </Button>
      </div>

      {result && result.status === "ready" && (
        <div className="mt-6 rounded-2xl border border-match/30 bg-match-soft p-6">
          <p className="text-sm font-medium text-match">Resume processed</p>
          <p className="mt-1 text-sm text-ink/70">
            Extracted {result.char_count?.toLocaleString()} characters from{" "}
            {result.original_filename}.
          </p>
        </div>
      )}

      {history.length > 0 && (
        <div className="mt-8">
          <h2 className="text-sm font-medium text-ink/70">
            Previously uploaded
          </h2>
          <ul className="mt-3 space-y-2">
            {history.map((r) => (
              <li
                key={r.id}
                className="flex items-center justify-between rounded-lg border border-line bg-white px-4 py-3 text-sm"
              >
                <span className="text-ink/80">{r.original_filename}</span>
                <span
                  className={
                    r.status === "ready"
                      ? "rounded-full bg-match-soft px-2 py-0.5 text-xs font-medium text-match"
                      : "rounded-full bg-gap-soft px-2 py-0.5 text-xs font-medium text-gap"
                  }
                >
                  {r.status === "ready" ? "Ready" : "Failed"}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}