import type { SkillGap, GapAnalysis } from "@/lib/api";

function GapRow({ gap }: { gap: SkillGap }) {
  const toneClass =
    gap.status === "matched"
      ? "bg-match-soft text-match"
      : gap.status === "partial"
        ? "bg-signal-soft text-signal"
        : "bg-gap-soft text-gap";

  return (
    <li className="flex items-start justify-between gap-4 rounded-lg border border-line bg-white px-4 py-3">
      <div>
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-ink">{gap.skill}</span>
          <span className="text-xs text-ink/40">
            {gap.importance === "required" ? "Required" : "Preferred"}
          </span>
        </div>
        {gap.evidence && (
          <p className="mt-1 text-xs text-ink/50">{gap.evidence}</p>
        )}
      </div>
      <span className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-medium ${toneClass}`}>
        {gap.status === "matched" ? "Matched" : gap.status === "partial" ? "Partial" : "Missing"}
      </span>
    </li>
  );
}

export function GapAnalysisCard({ gapAnalysis }: { gapAnalysis: GapAnalysis }) {
  const missing = gapAnalysis.gaps.filter((g) => g.status === "missing");
  const partial = gapAnalysis.gaps.filter((g) => g.status === "partial");
  const matched = gapAnalysis.gaps.filter((g) => g.status === "matched");

  return (
    <div className="rounded-2xl border border-line bg-white p-6">
      <h2 className="text-lg text-navy">Skill gaps</h2>
      <p className="mt-1 text-sm text-ink/60">
        Ordered by priority — required skills you&apos;re missing entirely
        matter most; skills you&apos;ve only touched in a project count as
        partial evidence, not a full match.
      </p>

      {missing.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-medium text-gap">
            Missing ({missing.length})
          </h3>
          <ul className="mt-2 space-y-2">
            {missing.map((g) => (
              <GapRow key={g.skill} gap={g} />
            ))}
          </ul>
        </div>
      )}

      {partial.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-medium text-signal">
            Partial evidence ({partial.length})
          </h3>
          <ul className="mt-2 space-y-2">
            {partial.map((g) => (
              <GapRow key={g.skill} gap={g} />
            ))}
          </ul>
        </div>
      )}

      {matched.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-medium text-match">
            Matched ({matched.length})
          </h3>
          <ul className="mt-2 space-y-2">
            {matched.map((g) => (
              <GapRow key={g.skill} gap={g} />
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}