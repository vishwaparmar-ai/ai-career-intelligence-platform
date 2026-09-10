import { ResumeUploadPanel } from "@/components/resume-upload-panel";
import { JobInputPanel } from "@/components/job-input-panel";
import { AnalysisPanel } from "@/components/analysis-panel";

export default function DashboardOverviewPage() {
  return (
    <div>
      <h1 className="text-2xl text-navy">Overview</h1>
      <p className="mt-2 text-sm text-ink/60">
        Upload a resume and paste a job description below to generate your
        first readiness score.
      </p>

      <div className="mt-8 flex flex-col gap-12">
        <ResumeUploadPanel compact />
        <JobInputPanel compact />
      </div>

      <div className="mt-12">
        <AnalysisPanel />
      </div>

      <div className="mt-12">
        <section className="rounded-2xl border border-line bg-white p-6 md:max-w-sm">
          <h2 className="text-sm font-medium text-ink/70">Interview practice</h2>
          <p className="mt-4 text-sm text-ink/50">
            Job-specific interview questions unlock after your first
            analysis.
          </p>
        </section>
      </div>
    </div>
  );
}