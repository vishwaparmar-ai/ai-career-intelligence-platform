export default function DashboardOverviewPage() {
  return (
    <div>
      <h1 className="text-2xl text-navy">Overview</h1>
      <p className="mt-2 text-sm text-ink/60">
        Upload a resume and a job description to generate your first
        readiness score.
      </p>

      <div className="mt-8 grid gap-6 md:grid-cols-2">
        <section className="rounded-2xl border border-line bg-white p-6">
          <h2 className="text-sm font-medium text-ink/70">Readiness score</h2>
          <p className="mt-4 text-sm text-ink/50">
            No analysis yet. Add a resume and a job description to see your
            score here.
          </p>
        </section>

        <section className="rounded-2xl border border-line bg-white p-6">
          <h2 className="text-sm font-medium text-ink/70">Skill gaps</h2>
          <p className="mt-4 text-sm text-ink/50">
            Matched, partial, and missing skills will show up here once a
            job is analyzed.
          </p>
        </section>

        <section className="rounded-2xl border border-line bg-white p-6">
          <h2 className="text-sm font-medium text-ink/70">30-day roadmap</h2>
          <p className="mt-4 text-sm text-ink/50">
            Your prioritized plan is generated from your specific gaps —
            nothing to show until then.
          </p>
        </section>

        <section className="rounded-2xl border border-line bg-white p-6">
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
