import type { Metadata } from "next";
import { Fraunces, IBM_Plex_Sans } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-fraunces",
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
});

const plexSans = IBM_Plex_Sans({
  subsets: ["latin"],
  variable: "--font-plex",
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "CareerIQ — Know exactly where you stand for the job",
  description:
    "Upload your resume and a job description. Get an evidence-backed readiness score, the gaps that matter, and a plan to close them.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${fraunces.variable} ${plexSans.variable}`}>
      <body className="flex min-h-screen flex-col">
        <header className="border-b border-line">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
            <Link href="/" className="font-display text-lg font-medium text-navy">
              CareerIQ
            </Link>
            <nav className="flex items-center gap-6 text-sm">
              <Link href="/login" className="text-ink/70 hover:text-ink">
                Log in
              </Link>
              <Link
                href="/signup"
                className="rounded-full bg-navy px-4 py-2 text-paper transition-colors hover:bg-navy-light"
              >
                Get your score
              </Link>
            </nav>
          </div>
        </header>

        <main className="flex-1">{children}</main>

        <footer className="border-t border-line">
          <div className="mx-auto max-w-6xl px-6 py-6 text-sm text-ink/60">
            CareerIQ — a readiness engine for job seekers.
          </div>
        </footer>
      </body>
    </html>
  );
}
