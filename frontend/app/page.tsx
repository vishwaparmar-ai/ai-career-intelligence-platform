import Link from "next/link";

const steps = [
  {
    n: "1",
    title: "Create a free account",
    body: "Sign up, then upload a resume and paste the job description you're aiming for — right in your dashboard.",
  },
  {
    n: "2",
    title: "See what actually matches",
    body: "Required skills, experience, and projects get compared against the job — not guessed at. Every match or gap traces back to a line in your resume.",
  },
  {
    n: "3",
    title: "Get a plan to close the gap",
    body: "A prioritized, 30-day plan built from your specific gaps, plus interview questions pulled from the same job description.",
  },
];

const benefits = [
  {
    title: "Evidence-backed, not a black box",
    body: "Every matched or missing skill traces back to a specific line in your resume or the posting — never a vague AI guess.",
  },
  {
    title: "Built for your next application",
    body: "Paste in the actual job you're going for. The gaps and roadmap are specific to that posting, not generic career advice.",
  },
  {
    title: "Practice for the interview it leads to",
    body: "Once your gaps are known, get interview questions pulled from the same job description — not a random question bank.",
  },
];

export default function LandingPage() {
  return (
    <div className="mx-auto max-w-6xl px-6">
      <section className="grid gap-12 py-20 md:grid-cols-2 md:items-center md:py-28">
        <div>
          <h1 className="max-w-md text-4xl leading-[1.1] text-navy md:text-5xl">
            Know exactly where you stand for the job.
          </h1>
          <p className="mt-6 max-w-prose text-ink/70">
            CareerIQ reads your resume against a real job description and
            explains the score: what matches, what&apos;s missing, and the
            shortest practical path to close the gap.
          </p>
          <div className="mt-8 flex items-center gap-4">
            <Link
              href="/signup"
              className="rounded-full bg-navy px-6 py-3 text-sm font-medium text-paper transition-colors hover:bg-navy-light"
            >
              Get your score
            </Link>
            <Link href="/login" className="text-sm text-ink/70 hover:text-ink">
              I already have an account
            </Link>
          </div>
        </div>

        <div className="rounded-2xl border border-line bg-white p-6 shadow-sm">
          <div className="flex items-baseline justify-between">
            <span className="text-sm text-ink/60">Readiness for Backend Engineer</span>
            <span className="font-display text-3xl text-navy">76%</span>
          </div>
          <div className="mt-4 h-2 w-full overflow-hidden rounded-full bg-line">
            <div className="h-full w-3/4 rounded-full bg-navy" />
          </div>

          <dl className="mt-6 space-y-3 text-sm">
            <div className="flex items-start gap-3">
              <span className="mt-0.5 rounded-full bg-match-soft px-2 py-0.5 text-xs font-medium text-match">
                Matched
              </span>
              <span className="text-ink/80">FastAPI, PostgreSQL, REST API design</span>
            </div>
            <div className="flex items-start gap-3">
              <span className="mt-0.5 rounded-full bg-signal-soft px-2 py-0.5 text-xs font-medium text-signal">
                Partial
              </span>
              <span className="text-ink/80">AWS deployment — one project, no CI/CD</span>
            </div>
            <div className="flex items-start gap-3">
              <span className="mt-0.5 rounded-full bg-gap-soft px-2 py-0.5 text-xs font-medium text-gap">
                Missing
              </span>
              <span className="text-ink/80">Kubernetes, event-driven architecture</span>
            </div>
          </dl>
          <p className="mt-4 text-xs text-ink/40">
            Example output — sign up to run your own.
          </p>
        </div>
      </section>

      <section className="border-t border-line py-16">
        <h2 className="text-2xl text-navy">How it works</h2>
        <div className="mt-10 grid gap-10 md:grid-cols-3">
          {steps.map((step) => (
            <div key={step.n}>
              <span className="font-display text-2xl text-signal">{step.n}</span>
              <h3 className="mt-3 text-lg text-ink">{step.title}</h3>
              <p className="mt-2 text-sm text-ink/70">{step.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="border-t border-line py-16">
        <h2 className="text-2xl text-navy">Why CareerIQ</h2>
        <div className="mt-10 grid gap-10 md:grid-cols-3">
          {benefits.map((b) => (
            <div key={b.title}>
              <h3 className="text-lg text-ink">{b.title}</h3>
              <p className="mt-2 text-sm text-ink/70">{b.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="border-t border-line py-16 text-center">
        <h2 className="text-2xl text-navy">
          See your readiness for the job you actually want.
        </h2>
        <p className="mx-auto mt-3 max-w-md text-sm text-ink/60">
          Free to start. Takes a couple of minutes once you're signed in.
        </p>
        <Link
          href="/signup"
          className="mt-6 inline-block rounded-full bg-navy px-6 py-3 text-sm font-medium text-paper transition-colors hover:bg-navy-light"
        >
          Get your score
        </Link>
      </section>
    </div>
  );
}