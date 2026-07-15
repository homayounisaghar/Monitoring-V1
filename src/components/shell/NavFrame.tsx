import { Link, useNavigate, useRouterState } from "@tanstack/react-router";
import { Search, Bell, Settings, ChevronDown } from "lucide-react";
import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
} from "@/components/ui/dropdown-menu";

const TABS = [
  { to: "/session", label: "Session" },
  { to: "/athlete", label: "Athlete" },
  { to: "/longitudinal", label: "Longitudinal" },
] as const;

const SQUADS = ["First Team", "Under-23s", "Women's"] as const;

export function NavFrame() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const [squad, setSquad] = useState<string>(SQUADS[0]);
  const navigate = useNavigate();
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => setEmail(data.session?.user.email ?? null));
    const { data: sub } = supabase.auth.onAuthStateChange((_e, session) => {
      setEmail(session?.user.email ?? null);
    });
    return () => sub.subscription.unsubscribe();
  }, []);

  const initials = email
    ? email
        .split("@")[0]
        .split(/[._-]/)
        .map((s) => s[0]?.toUpperCase() ?? "")
        .join("")
        .slice(0, 2) || "U"
    : "";

  async function onSignOut() {
    await supabase.auth.signOut();
    navigate({ to: "/auth" });
  }


  return (
    <header
      className="sticky top-0 z-40 h-12 border-b"
      style={{
        
        backgroundColor: "var(--color-surface-card)",
        borderColor: "var(--color-border)",
      }}
    >
      <div className="mx-auto grid h-full max-w-[1320px] grid-cols-[auto_1fr_auto] items-center gap-6 px-6">
        {/* LEFT — brand + team context */}
        <div className="flex items-center gap-3">
          <Link to="/session" className="flex items-center gap-2" aria-label="ST2 home">
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

          {/* Divider between brand and context */}
          <span
            aria-hidden
            className="h-4 w-px"
            style={{ backgroundColor: "var(--color-border)" }}
          />

          {/* Team selector — quiet, subordinate */}
          <DropdownMenu>
            <DropdownMenuTrigger
              className="flex h-8 items-center gap-1 rounded-md px-2 text-[12.5px] font-medium outline-none transition-colors hover:bg-[var(--color-canvas)] focus-visible:ring-2 focus-visible:ring-[var(--color-brand)] focus-visible:ring-offset-1"
              style={{ color: "var(--color-text-secondary)" }}
              aria-label="Select team"
            >
              <span>{squad}</span>
              <ChevronDown className="h-3.5 w-3.5 opacity-70" aria-hidden />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="min-w-[180px]">
              <DropdownMenuLabel>Team</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuRadioGroup value={squad} onValueChange={setSquad}>
                {SQUADS.map((s) => (
                  <DropdownMenuRadioItem key={s} value={s}>
                    {s}
                  </DropdownMenuRadioItem>
                ))}
              </DropdownMenuRadioGroup>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* CENTER — primary navigation, optically balanced across the bar */}
        <nav className="flex items-center justify-center gap-8" aria-label="Primary">
          {TABS.map((t) => {
            const active =
              pathname === t.to || (t.to === "/session" && pathname === "/");
            return (
              <Link
                key={t.to}
                to={t.to}
                className="relative flex h-12 items-center text-[13px] font-medium transition-colors"
                style={{
                  color: active
                    ? "var(--color-text-primary)"
                    : "var(--color-text-secondary)",
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

        {/* RIGHT — utility cluster */}
        <div className="flex items-center gap-1.5">
          {/* Search */}
          <div
            className="flex h-8 w-56 items-center gap-2 rounded-md border px-2.5"
            style={{
              borderColor: "var(--color-border)",
              backgroundColor: "var(--color-canvas)",
            }}
          >
            <Search
              className="h-3.5 w-3.5"
              style={{ color: "var(--color-text-tertiary)" }}
              aria-hidden
            />
            <input
              type="search"
              placeholder="Search athletes, sessions…"
              aria-label="Search athletes and sessions"
              className="w-full bg-transparent text-[12.5px] outline-none placeholder:opacity-70"
              style={{ color: "var(--color-text-primary)" }}
            />
          </div>

          {/* Notifications */}
          <button
            type="button"
            aria-label="Notifications"
            className="relative grid h-8 w-8 place-items-center rounded-md outline-none transition-colors hover:bg-[var(--color-canvas)] focus-visible:ring-2 focus-visible:ring-[var(--color-brand)] focus-visible:ring-offset-1"
            style={{ color: "var(--color-text-secondary)" }}
          >
            <Bell className="h-4 w-4" aria-hidden />
            <span
              aria-hidden
              className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full"
              style={{ backgroundColor: "var(--color-text-secondary)" }}
            />
            <span className="sr-only">Unread notifications</span>
          </button>

          {/* Settings */}
          <button
            type="button"
            aria-label="Settings"
            className="grid h-8 w-8 place-items-center rounded-md outline-none transition-colors hover:bg-[var(--color-canvas)] focus-visible:ring-2 focus-visible:ring-[var(--color-brand)] focus-visible:ring-offset-1"
            style={{ color: "var(--color-text-secondary)" }}
          >
            <Settings className="h-4 w-4" aria-hidden />
          </button>

          {/* Hairline separator before identity */}
          <span
            aria-hidden
            className="mx-1.5 h-5 w-px"
            style={{ backgroundColor: "var(--color-border)" }}
          />

          {/* Account */}
          {email ? (
            <DropdownMenu>
              <DropdownMenuTrigger
                className="grid h-8 w-8 place-items-center rounded-full outline-none transition-opacity hover:opacity-90 focus-visible:ring-2 focus-visible:ring-[var(--color-brand)] focus-visible:ring-offset-1"
                style={{ backgroundColor: "var(--color-brand)" }}
                aria-label="Account menu"
              >
                <span
                  className="text-[11px] font-semibold"
                  style={{ color: "var(--color-text-on-brand)" }}
                >
                  {initials}
                </span>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="min-w-[200px]">
                <DropdownMenuLabel className="truncate">{email}</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onSelect={onSignOut}>Sign out</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Link
              to="/auth"
              className="inline-flex h-8 items-center rounded-md px-3 text-[12.5px] font-medium outline-none transition-colors hover:bg-[var(--color-canvas)] focus-visible:ring-2 focus-visible:ring-[var(--color-brand)] focus-visible:ring-offset-1"
              style={{ color: "var(--color-text-primary)" }}
            >
              Sign in
            </Link>
          )}

        </div>
      </div>
    </header>

  );
}
