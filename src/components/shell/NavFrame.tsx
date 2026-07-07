import { Link, useRouterState } from "@tanstack/react-router";
import { Search } from "lucide-react";

const TABS = [
  { to: "/session",      label: "Session" },
  { to: "/athlete",      label: "Athlete" },
  { to: "/longitudinal", label: "Longitudinal" },
] as const;

export function NavFrame() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <header
      className="sticky top-0 z-40 h-12 border-b"
      style={{
        backgroundColor: "var(--color-surface-card)",
        borderColor: "var(--color-border)",
      }}
    >
      <div className="mx-auto flex h-full max-w-[1320px] items-center gap-8 px-6">
        {/* Logo — brand mark */}
        <Link to="/session" className="flex items-center gap-2">
          <span
            className="grid h-6 w-6 place-items-center rounded"
            style={{ backgroundColor: "var(--color-brand)" }}
            aria-hidden
          >
            <span
              className="text-[11px] font-bold"
              style={{ color: "var(--color-text-on-brand)" }}
            >
              S
            </span>
          </span>
          <span
            className="text-[13px] font-semibold tracking-tight"
            style={{ color: "var(--color-text-primary)" }}
          >
            ST2
          </span>
        </Link>

        {/* Tabs — the only green-underline idiom in the product */}
        <nav className="flex items-center gap-6" aria-label="Primary">
          {TABS.map((t) => {
            const active = pathname === t.to || (t.to === "/session" && pathname === "/");
            return (
              <Link
                key={t.to}
                to={t.to}
                className="relative flex h-12 items-center text-[13px] font-medium transition-colors"
                style={{
                  color: active ? "var(--color-text-primary)" : "var(--color-text-secondary)",
                }}
              >
                {t.label}
                {active && (
                  <span
                    className="absolute inset-x-0 bottom-0 h-[2px]"
                    style={{ backgroundColor: "var(--color-brand)" }}
                    aria-hidden
                  />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Search — right */}
        <div className="ml-auto flex items-center">
          <div
            className="flex h-8 w-64 items-center gap-2 rounded-md border px-2.5"
            style={{
              borderColor: "var(--color-border)",
              backgroundColor: "var(--color-canvas)",
            }}
          >
            <Search className="h-3.5 w-3.5" style={{ color: "var(--color-text-tertiary)" }} />
            <input
              type="search"
              placeholder="Search athletes, sessions…"
              className="w-full bg-transparent text-[12.5px] outline-none placeholder:opacity-70"
              style={{ color: "var(--color-text-primary)" }}
            />
          </div>
        </div>
      </div>
    </header>
  );
}
