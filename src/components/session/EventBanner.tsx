import { Pencil, Share2 } from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { currentSession } from "@/lib/session-data";
import { copy } from "@/lib/copy-deck";

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
      <div className="flex h-[52px] items-center justify-between gap-6 px-5">
        {/* Left — identity, single line */}
        <div className="flex min-w-0 items-baseline gap-x-2.5 truncate">
          <h1 className="truncate text-[16px] font-semibold tracking-tight">
            {s.label}{s.result ? ` · ${s.result}` : ""}
          </h1>
          <span
            className="type-microcaps rounded px-1.5 py-0.5"
            style={{
              backgroundColor: "color-mix(in oklab, white 12%, transparent)",
              color: "var(--color-slate-300)",
            }}
          >
            {s.kind === "match" ? copy("canonical.eventBanner.match") : copy("canonical.eventBanner.training")}
          </span>
          <span
            className="whitespace-nowrap text-[12.5px]"
            style={{ color: "var(--color-slate-300)" }}
          >
            {formatDate(s.dateISO)}
            <Sep />
            <span className="type-num">{s.durationMin}' total</span>
            {s.venue && (
              <>
                <Sep />
                {s.venue}
              </>
            )}
            {s.weather && (
              <>
                <Sep />
                <span className="type-num">
                  {s.weather.tempC}°C · {s.weather.humidityPct}% RH
                </span>
              </>
            )}
          </span>
        </div>

        {/* Right — icon-only actions */}
        <div className="flex items-center gap-1" ref={menuRef}>
          <IconBtn label={copy("canonical.eventBanner.editSession")}>
            <Pencil className="h-3.5 w-3.5" />
          </IconBtn>
          <div className="relative">
            <IconBtn label={copy("canonical.eventBanner.shareExport")} onClick={() => setMenuOpen((o) => !o)}>
              <Share2 className="h-3.5 w-3.5" />
            </IconBtn>
            {menuOpen && (
              <div
                className="absolute right-0 top-9 z-30 w-40 overflow-hidden rounded-md border shadow-lg"
                style={{
                  backgroundColor: "var(--color-surface-card)",
                  borderColor: "var(--color-border)",
                  color: "var(--color-text-primary)",
                }}
              >
                {[copy("canonical.eventBanner.exportCsv"), copy("canonical.eventBanner.exportPdf"), copy("canonical.eventBanner.copyLink")].map((label) => (
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

function Sep() {
  return (
    <span className="mx-1.5" style={{ color: "var(--color-slate-500)" }}>
      ·
    </span>
  );
}

function IconBtn({
  children,
  label,
  onClick,
}: {
  children: React.ReactNode;
  label: string;
  onClick?: () => void;
}) {
  return (
    <button
      onClick={onClick}
      aria-label={label}
      title={label}
      className="grid h-8 w-8 place-items-center rounded transition-colors"
      style={{ color: "var(--color-slate-300)" }}
      onMouseEnter={(e) =>
        (e.currentTarget.style.backgroundColor =
          "color-mix(in oklab, white 8%, transparent)")
      }
      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
    >
      {children}
    </button>
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
