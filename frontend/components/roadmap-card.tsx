import type { RoadmapData } from "@/lib/api";

const PRIORITY_STYLES: Record<string, string> = {
  high: "bg-gap-soft text-gap",
  medium: "bg-signal-soft text-signal",
  low: "bg-match-soft text-match",
};

export function RoadmapCard({ roadmap }: { roadmap: RoadmapData }) {
  return (
    <div className="rounded-2xl border border-line bg-white p-6">
      <h2 className="text-lg text-navy">Your 30-day roadmap</h2>
      <p className="mt-1 text-sm text-ink/60">
        Ordered by priority — start from the top.
      </p>

      <ol className="mt-4 space-y-4">
        {roadmap.items.map((item, i) => (
          <li key={i} className="rounded-lg border border-line p-4">
            <div className="flex items-center justify-between gap-4">
              <span className="text-sm font-medium text-ink">
                {i + 1}. {item.skill}
              </span>
              {item.priority && (
                <span
                  className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-medium ${
                    PRIORITY_STYLES[item.priority.toLowerCase()] ??
                    "bg-navy/5 text-navy"
                  }`}
                >
                  {item.priority}
                </span>
              )}
            </div>

            {item.reason && (
              <p className="mt-2 text-sm text-ink/70">{item.reason}</p>
            )}

            {item.effort && (
              <p className="mt-2 text-xs text-ink/50">
                <span className="font-medium text-ink/70">Effort:</span>{" "}
                {item.effort}
              </p>
            )}

            {item.practical_task && (
              <p className="mt-3 rounded-lg bg-navy/5 p-3 text-sm text-ink/80">
                <span className="font-medium text-ink">Try this:</span>{" "}
                {item.practical_task}
              </p>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}