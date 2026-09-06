import type { CandidateProfileData } from "@/lib/api";

export function CandidateProfileCard({ data }: { data: CandidateProfileData }) {
  return (
    <div className="mt-6 rounded-2xl border border-line bg-white p-6">
      <h2 className="text-lg text-navy">Extracted profile</h2>

      <section className="mt-4">
        <h3 className="text-sm font-medium text-ink/70">Skills</h3>
        {data.skills.length === 0 ? (
          <p className="mt-1 text-sm text-ink/50">None found.</p>
        ) : (
          <div className="mt-2 flex flex-wrap gap-2">
            {data.skills.map((skill) => (
              <span
                key={skill}
                className="rounded-full bg-navy/5 px-3 py-1 text-xs text-navy"
              >
                {skill}
              </span>
            ))}
          </div>
        )}
      </section>

      <section className="mt-6">
        <h3 className="text-sm font-medium text-ink/70">Experience</h3>
        {data.experience.length === 0 ? (
          <p className="mt-1 text-sm text-ink/50">None found.</p>
        ) : (
          <ul className="mt-2 space-y-3">
            {data.experience.map((exp, i) => (
              <li key={i} className="text-sm">
                <p className="font-medium text-ink">
                  {exp.title} · {exp.company}
                </p>
                {(exp.start_date || exp.end_date) && (
                  <p className="text-xs text-ink/50">
                    {exp.start_date ?? "?"} – {exp.end_date ?? "?"}
                  </p>
                )}
                {exp.description.length > 0 && (
                  <ul className="mt-1 list-disc space-y-0.5 pl-4 text-ink/70">
                    {exp.description.map((line, j) => (
                      <li key={j}>{line}</li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mt-6">
        <h3 className="text-sm font-medium text-ink/70">Education</h3>
        {data.education.length === 0 ? (
          <p className="mt-1 text-sm text-ink/50">None found.</p>
        ) : (
          <ul className="mt-2 space-y-2">
            {data.education.map((edu, i) => (
              <li key={i} className="text-sm">
                <p className="font-medium text-ink">
                  {edu.degree} · {edu.institution}
                </p>
                {(edu.start_date || edu.end_date) && (
                  <p className="text-xs text-ink/50">
                    {edu.start_date ?? "?"} – {edu.end_date ?? "?"}
                  </p>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mt-6">
        <h3 className="text-sm font-medium text-ink/70">Projects</h3>
        {data.projects.length === 0 ? (
          <p className="mt-1 text-sm text-ink/50">None found.</p>
        ) : (
          <ul className="mt-2 space-y-2">
            {data.projects.map((proj, i) => (
              <li key={i} className="text-sm">
                <p className="font-medium text-ink">{proj.name}</p>
                {proj.description.length > 0 && (
                  <ul className="mt-1 list-disc space-y-0.5 pl-4 text-ink/70">
                    {proj.description.map((line, j) => (
                      <li key={j}>{line}</li>
                    ))}
                  </ul>
                )}
                {proj.technologies.length > 0 && (
                  <p className="mt-1 text-xs text-ink/50">
                    {proj.technologies.join(", ")}
                  </p>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mt-6">
        <h3 className="text-sm font-medium text-ink/70">Certifications</h3>
        {data.certifications.length === 0 ? (
          <p className="mt-1 text-sm text-ink/50">None found.</p>
        ) : (
          <ul className="mt-2 space-y-1 text-sm">
            {data.certifications.map((cert, i) => (
              <li key={i} className="text-ink/80">
                {cert.title ?? "Untitled certification"}
                {cert.issuer ? ` · ${cert.issuer}` : ""}
                {cert.date ? ` (${cert.date})` : ""}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}