"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { clearToken } from "@/lib/auth";

const links = [
  { href: "/dashboard", label: "Overview" },
  { href: "/dashboard/resume", label: "Resume" },
  { href: "/dashboard/job", label: "Job analysis" },
  { href: "/dashboard/roadmap", label: "Roadmap" },
  { href: "/dashboard/interview", label: "Interview" },
];

export function DashboardSidebar() {
  const pathname = usePathname();
  const router = useRouter();

  function handleLogout() {
    clearToken();
    router.replace("/login");
  }

  return (
    <nav className="flex h-full flex-col justify-between p-4">
      <div className="flex flex-col gap-1">
        {links.map((link) => {
          const active = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "rounded-lg px-3 py-2 text-sm transition-colors",
                active
                  ? "bg-navy text-paper"
                  : "text-ink/70 hover:bg-navy/5 hover:text-ink"
              )}
            >
              {link.label}
            </Link>
          );
        })}
      </div>

      <button
        onClick={handleLogout}
        className="rounded-lg px-3 py-2 text-left text-sm text-ink/60 transition-colors hover:bg-gap-soft hover:text-gap"
      >
        Log out
      </button>
    </nav>
  );
}