import { Pencil, Share2, ChevronDown } from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { currentSession } from "@/lib/session-data";

export function EventBanner() {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!menuOpen) return;
    const onDoc = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setMenuOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [menuOpen]);

  const s = currentSession;

  return (
    <div
      className="rounded-lg"
      style={{
        backgroundColor: "var(--color-chrome)",
        color: "var(--color-text-on-brand)",
      }}
    >
      <div className="flex items-center justify-between gap-6 px-6 py-4">
        {/* Left — identity */}
        <div className="flex min-w-0 flex-wrap items-baseline gap-x-3 gap-y-1">
          <h1 className="text-[18px] font-semibold tracking-tight">
            {s.label}{s.result ? ` · ${s.result}` : ""}
          </h1>
          <span
            className="type-microcaps rounded px-1.5 py-0.5"
            style={{
              backgroundColor: "color-mix(in oklab, white 12%, transparent)",
              color: "var(--color-slate-300)",
            }}
          >
            {s.kind === "match" ? "Match" : "Training"}
          </span>
          <span
            className="text-[12.5px]"
            style={{ color: "var(--color-slate-300)" }}
          >
            {formatDate(s.dateISO)}
          </span>
          <span style={{ color: "var(--color-slate-500)" }}>·</span>
          <span
            className="type-num text-[12.5px]"
            style={{ color: "var(--color-slate-300)" }}
          >
            {s.durationMin}' total
          </span>
          {s.venue && (
            <>
              <span style={{ color: "var(--color-slate-500)" }}>·</span>
              <span className="text-[12.5px]" style={{ color: "var(--color-slate-300)" }}>
                {s.venue}
              </span>
            </>
          )}
          {s.weather && (
            <>
              <span style={{ color: "var(--color-slate-500)" }}>·</span>
              <span
                className="type-num text-[12.5px]"
                style={{ color: "var(--color-slate-400)" }}
              >
                {s.weather.tempC}°C · {s.weather.humidityPct}% RH
              </span>
            </>
          )}
        </div>

        {/* Right — one quiet action cluster */}
        <div className="flex items-center gap-1.5" ref={menuRef}>
          <button
            className="flex h-8 items-center gap-1.5 rounded px-2.5 text-[12.5px] transition-colors"
            style={{ color: "var(--color-slate-300)" }}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "color-mix(in oklab, white 8%, transparent)")}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
          >
            <Pencil className="h-3 w-3" />
            <span>Edit session</span>
          </button>

          <div className="relative">
            <button
              onClick={() => setMenuOpen((o) => !o)}
              aria-label="Share / export"
              className="grid h-8 w-8 place-items-center rounded transition-colors"
              style={{ color: "var(--color-slate-300)" }}
              onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "color-mix(in oklab, white 8%, transparent)")}
              onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
            >
              <Share2 className="h-3.5 w-3.5" />
            </button>
            {menuOpen && (
              <div
                className="absolute right-0 top-9 z-30 w-40 overflow-hidden rounded-md border shadow-lg"
                style={{
                  backgroundColor: "var(--color-surface-card)",
                  borderColor: "var(--color-border)",
                  color: "var(--color-text-primary)",
                }}
              >
                {["Export CSV", "Export PDF", "Copy link"].map((label) => (
                  <button
                    key={label}
                    className="block w-full px-3 py-2 text-left text-[12.5px] transition-colors hover:bg-[color:var(--color-slate-100)]"
                  >
                    {label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function formatDate(iso: string) {
  const d = new Date(iso);
  return d.toLocaleDateString("en-GB", {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}
