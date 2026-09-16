import { ResumeUploadPanel } from "@/components/resume-upload-panel";
import { JobInputPanel } from "@/components/job-input-panel";
import { AnalysisPanel } from "@/components/analysis-panel";
import { KnowledgeAskPanel } from "@/components/knowledge-ask-panel";

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
        <KnowledgeAskPanel />
      </div>
    </div>
  );
}