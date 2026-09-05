"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getCurrentUser, type CurrentUser } from "@/lib/api";
import { clearToken, getToken } from "@/lib/auth";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.replace("/login");
      return;
    }

    getCurrentUser(token)
      .then(setUser)
      .catch(() => {
        // Token is missing, expired, or invalid — clear it and send them back.
        clearToken();
        router.replace("/login");
      })
      .finally(() => setChecking(false));
  }, [router]);

  if (checking) {
    return (
      <div className="px-6 py-10 text-sm text-ink/60">
        Checking your session…
      </div>
    );
  }

  if (!user) {
    // Redirect is already in flight; render nothing to avoid a flash of content.
    return null;
  }

  return <>{children}</>;
}