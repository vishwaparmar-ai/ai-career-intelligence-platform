import { ResumeUploadPanel } from "@/components/resume-upload-panel";
import { JobInputPanel } from "@/components/job-input-panel";
import { AnalysisPanel } from "@/components/analysis-panel";
import { KnowledgeAskPanel } from "@/components/knowledge-ask-panel";

function StepLabel({ n, children }: { n: number; children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-ink/40">
      <span className="flex h-5 w-5 items-center justify-center rounded-full bg-navy/10 text-navy">
        {n}
      </span>
      {children}
    </div>
  );
}

export default function DashboardOverviewPage() {
  return (
    <div>
      <h1 className="text-2xl text-navy">Your Job Readiness Engine</h1>
      <p className="mt-2 text-sm text-ink/60">
        Resume in, job description in, an evidence-backed score out —
        with the gaps, roadmap, and interview practice to close them.
      </p>

      <div className="mt-10 flex flex-col gap-6">
        <StepLabel n={1}>Your inputs</StepLabel>
        <div className="flex flex-col gap-8">
          <ResumeUploadPanel compact />
          <JobInputPanel compact />
        </div>
      </div>

      <div className="mt-12 flex flex-col gap-6">
        <StepLabel n={2}>Your readiness</StepLabel>
        <AnalysisPanel />
      </div>

      <div className="mt-12">
        <KnowledgeAskPanel />
      </div>
    </div>
  );
}