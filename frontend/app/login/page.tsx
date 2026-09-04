"use client";

import { useState } from "react";
import Link from "next/link";
import { Field } from "@/components/ui/field";
import { Button } from "@/components/ui/button";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);

    // TODO (Day 11): replace with a real call to
    // `${process.env.NEXT_PUBLIC_API_URL}/auth/login`
    console.log("login submit", { email, password });

    setTimeout(() => setSubmitting(false), 400);
  }

  return (
    <div className="mx-auto flex max-w-sm flex-col justify-center px-6 py-20">
      <h1 className="text-2xl text-navy">Log in</h1>
      <p className="mt-2 text-sm text-ink/60">
        Pick up where your readiness analysis left off.
      </p>

      <form onSubmit={handleSubmit} className="mt-8 flex flex-col gap-4">
        <Field
          label="Email"
          type="email"
          name="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <Field
          label="Password"
          type="password"
          name="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <Button type="submit" disabled={submitting} className="mt-2">
          {submitting ? "Logging in…" : "Log in"}
        </Button>
      </form>

      <p className="mt-6 text-sm text-ink/60">
        New here?{" "}
        <Link href="/signup" className="font-medium text-navy hover:underline">
          Create an account
        </Link>
      </p>
    </div>
  );
}
