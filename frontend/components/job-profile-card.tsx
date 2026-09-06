import type { JobProfileData } from "@/lib/api";

export function JobProfileCard({ data }: { data: JobProfileData }) {
  return (
    <div className="mt-6 rounded-2xl border border-line bg-white p-6">
      <h2 className="text-lg text-navy">Extracted requirements</h2>

      <div className="mt-4 flex flex-wrap gap-6 text-sm">
        <div>
          <h3 className="font-medium text-ink/70">Seniority</h3>
          <p className="mt-1 text-ink">{data.seniority ?? "Not specified"}</p>
        </div>
        <div>
          <h3 className="font-medium text-ink/70">Min. experience</h3>
          <p className="mt-1 text-ink">
            {data.min_years_experience !== null
              ? `${data.min_years_experience} years`
              : "Not specified"}
          </p>
        </div>
      </div>

      <section className="mt-6">
        <h3 className="text-sm font-medium text-ink/70">Required skills</h3>
        {data.required_skills.length === 0 ? (
          <p className="mt-1 text-sm text-ink/50">None found.</p>
        ) : (
          <div className="mt-2 flex flex-wrap gap-2">
            {data.required_skills.map((skill) => (
              <span
                key={skill}
                className="rounded-full bg-gap-soft px-3 py-1 text-xs text-gap"
              >
                {skill}
              </span>
            ))}
          </div>
        )}
      </section>

      <section className="mt-6">
        <h3 className="text-sm font-medium text-ink/70">Preferred skills</h3>
        {data.preferred_skills.length === 0 ? (
          <p className="mt-1 text-sm text-ink/50">None found.</p>
        ) : (
          <div className="mt-2 flex flex-wrap gap-2">
            {data.preferred_skills.map((skill) => (
              <span
                key={skill}
                className="rounded-full bg-signal-soft px-3 py-1 text-xs text-signal"
              >
                {skill}
              </span>
            ))}
          </div>
        )}
      </section>

      <section className="mt-6">
        <h3 className="text-sm font-medium text-ink/70">Responsibilities</h3>
        {data.responsibilities.length === 0 ? (
          <p className="mt-1 text-sm text-ink/50">None found.</p>
        ) : (
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-ink/80">
            {data.responsibilities.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        )}
      </section>

      <section className="mt-6">
        <h3 className="text-sm font-medium text-ink/70">
          Education requirements
        </h3>
        {data.education_requirements.length === 0 ? (
          <p className="mt-1 text-sm text-ink/50">None found.</p>
        ) : (
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-ink/80">
            {data.education_requirements.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}