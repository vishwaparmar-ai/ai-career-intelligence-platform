import type { MatchResult } from "@/lib/api";

function ScoreBar({ label, score, weightPct }: { label: string; score: number; weightPct: number }) {
  return (
    <div>
      <div className="flex items-baseline justify-between text-sm">
        <span className="text-ink/80">
          {label}{" "}
          <span className="text-xs text-ink/40">({weightPct}% weight)</span>
        </span>
        <span className="font-medium text-navy">{Math.round(score * 100)}%</span>
      </div>
      <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-line">
        <div
          className="h-full rounded-full bg-navy"
          style={{ width: `${Math.round(score * 100)}%` }}
        />
      </div>
    </div>
  );
}

function SkillChips({ label, items, tone }: { label: string; items: string[]; tone: "match" | "gap" }) {
  if (items.length === 0) return null;
  const chipClass =
    tone === "match"
      ? "bg-match-soft text-match"
      : "bg-gap-soft text-gap";
  return (
    <div>
      <p className="text-xs font-medium text-ink/60">{label}</p>
      <div className="mt-1.5 flex flex-wrap gap-1.5">
        {items.map((item) => (
          <span key={item} className={`rounded-full px-2.5 py-1 text-xs ${chipClass}`}>
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}

export function MatchResultCard({ result }: { result: MatchResult }) {
  return (
    <div className="rounded-2xl border border-line bg-white p-6">
      <div className="flex items-baseline justify-between">
        <h2 className="text-lg text-navy">Readiness score</h2>
        <span className="font-display text-3xl text-navy">
          {result.overall_score}%
        </span>
      </div>

      <div className="mt-6 space-y-4">
        <ScoreBar
          label="Required skills"
          score={result.required_skills.score}
          weightPct={result.weights.required_skills * 100}
        />
        <ScoreBar
          label="Experience"
          score={result.experience.score}
          weightPct={result.weights.experience * 100}
        />
        <ScoreBar
          label="Projects"
          score={result.projects.score}
          weightPct={result.weights.projects * 100}
        />
        <ScoreBar
          label="Preferred skills"
          score={result.preferred_skills.score}
          weightPct={result.weights.preferred_skills * 100}
        />
        <ScoreBar
          label="Education"
          score={result.education.score}
          weightPct={result.weights.education * 100}
        />
        <ScoreBar
          label="Semantic similarity"
          score={result.semantic_score}
          weightPct={result.weights.semantic * 100}
        />
      </div>

      <div className="mt-6 space-y-4 border-t border-line pt-6">
        <SkillChips label="Matched required skills" items={result.required_skills.matched} tone="match" />
        <SkillChips label="Missing required skills" items={result.required_skills.missing} tone="gap" />
        <SkillChips label="Matched preferred skills" items={result.preferred_skills.matched} tone="match" />
      </div>

      <div className="mt-6 grid gap-4 border-t border-line pt-6 text-sm sm:grid-cols-2">
        <div>
          <p className="text-ink/60">Experience</p>
          <p className="mt-1 text-ink">
            {result.experience.candidate_years} years
            {result.experience.required_years !== null &&
              ` (job asks for ${result.experience.required_years}+)`}
          </p>
        </div>
        <div>
          <p className="text-ink/60">Education</p>
          <p className="mt-1 text-ink">
            {result.education.candidate_level ?? "Not specified"}
            {result.education.required_level &&
              ` (job asks for ${result.education.required_level})`}
          </p>
        </div>
      </div>
    </div>
  );
}