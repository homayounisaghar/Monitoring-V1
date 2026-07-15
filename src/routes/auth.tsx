import { createFileRoute, redirect, useNavigate, useSearch } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { lovable } from "@/integrations/lovable/index";

export const Route = createFileRoute("/auth")({
  ssr: false,
  validateSearch: (s: Record<string, unknown>) => ({
    next: typeof s.next === "string" ? s.next : "",
  }),
  beforeLoad: async ({ search }) => {
    const { data } = await supabase.auth.getSession();
    if (data.session) {
      const target = isSafeReturn(search.next) ? search.next : "/";
      throw redirect({ href: target });
    }
  },
  component: AuthPage,
});

function isSafeReturn(next: string): boolean {
  return typeof next === "string" && next.startsWith("/") && !next.startsWith("//");
}

function AuthPage() {
  const { next } = useSearch({ from: "/auth" });
  const navigate = useNavigate();
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const { data: sub } = supabase.auth.onAuthStateChange((event, session) => {
      if ((event === "SIGNED_IN" || event === "INITIAL_SESSION") && session) {
        const target = isSafeReturn(next) ? next : "/";
        window.location.replace(target);
      }
    });
    return () => sub.subscription.unsubscribe();
  }, [next]);

  async function onEmailSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      if (mode === "signup") {
        const { error } = await supabase.auth.signUp({
          email,
          password,
          options: { emailRedirectTo: window.location.origin + "/auth" },
        });
        if (error) throw error;
      } else {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
      }
      const target = isSafeReturn(next) ? next : "/";
      navigate({ href: target });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Sign-in failed");
    } finally {
      setBusy(false);
    }
  }

  async function onGoogle() {
    setError(null);
    setBusy(true);
    try {
      const returnTo = isSafeReturn(next) ? next : "/";
      if (returnTo !== "/") {
        try {
          sessionStorage.setItem("auth:next", returnTo);
        } catch {}
      }
      const result = await lovable.auth.signInWithOAuth("google", {
        redirect_uri: window.location.origin + "/auth",
      });
      if (result.error) throw result.error;
      if (result.redirected) return;
      const target = (() => {
        try {
          return sessionStorage.getItem("auth:next") ?? "/";
        } catch {
          return "/";
        }
      })();
      window.location.replace(target);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Google sign-in failed");
      setBusy(false);
    }
  }

  return (
    <main
      className="mx-auto flex min-h-[calc(100vh-3rem)] max-w-md flex-col justify-center px-6 py-12"
      style={{ backgroundColor: "var(--color-canvas)" }}
    >
      <h1 className="text-2xl font-semibold" style={{ color: "var(--color-text-primary)" }}>
        {mode === "signin" ? "Sign in to ST2" : "Create your ST2 account"}
      </h1>
      <p className="mt-1 text-sm" style={{ color: "var(--color-text-secondary)" }}>
        Sign in is required to authorize AI clients (ChatGPT, Claude, etc.) to
        read this app through its MCP server.
      </p>

      <button
        type="button"
        onClick={onGoogle}
        disabled={busy}
        className="mt-6 inline-flex w-full items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent disabled:opacity-50"
      >
        Continue with Google
      </button>

      <div className="my-6 flex items-center gap-3 text-xs" style={{ color: "var(--color-text-secondary)" }}>
        <span className="h-px flex-1" style={{ backgroundColor: "var(--color-border)" }} />
        or
        <span className="h-px flex-1" style={{ backgroundColor: "var(--color-border)" }} />
      </div>

      <form onSubmit={onEmailSubmit} className="space-y-3">
        <label className="block text-sm">
          <span style={{ color: "var(--color-text-secondary)" }}>Email</span>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 block w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          />
        </label>
        <label className="block text-sm">
          <span style={{ color: "var(--color-text-secondary)" }}>Password</span>
          <input
            type="password"
            required
            minLength={6}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 block w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          />
        </label>
        {error && (
          <p role="alert" className="text-sm text-red-600">
            {error}
          </p>
        )}
        <button
          type="submit"
          disabled={busy}
          className="inline-flex w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50"
        >
          {mode === "signin" ? "Sign in" : "Create account"}
        </button>
      </form>

      <button
        type="button"
        onClick={() => setMode(mode === "signin" ? "signup" : "signin")}
        className="mt-4 text-sm underline"
        style={{ color: "var(--color-text-secondary)" }}
      >
        {mode === "signin"
          ? "No account yet? Create one"
          : "Already have an account? Sign in"}
      </button>
    </main>
  );
}
