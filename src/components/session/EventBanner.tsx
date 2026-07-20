import { Pencil, Share2, Check } from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { currentSession } from "@/lib/session-data";
import { useSessionScope } from "@/lib/session-scope";
import { copy } from "@/lib/copy-deck";
import { weekdayDayMonthYear } from "@/lib/format-date";
import { buildShareUrl, isShareStateDefault, type ShareDefaults } from "@/lib/share-state";

const STATIC_DEFAULTS = {
  squadView: "table" as const,
  squadDisplay: "absolute" as const,
  squadSort: { key: "name" as const, dir: "asc" as const },
  squadChartMetric: "totalDistance" as const,
};

export function EventBanner() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [copied, setCopied] = useState(false);
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
  const scope = useSessionScope();
  const {
    dayCode,
    reference,
    benchmark,
    defaultReference,
    defaultBenchmark,
    filter,
    filterIsDefault,
    squadView,
    squadDisplay,
    squadSort,
    squadChartMetric,
  } = scope;

  const defaults: ShareDefaults = {
    reference: defaultReference.kind,
    benchmark: defaultBenchmark.kind,
    ...STATIC_DEFAULTS,
  };

  const shareState = {
    reference: reference.kind,
    benchmark: benchmark.kind,
    filter,
    squadView,
    squadDisplay,
    squadSort,
    squadChartMetric,
  };
  const isDefault = isShareStateDefault(
    {
      reference: reference.kind,
      benchmark: benchmark.kind,
      squadView,
      squadDisplay,
      squadSort,
      squadChartMetric,
    },
    defaults,
    filterIsDefault,
  );

  const handleCopyLink = async () => {
    if (typeof window === "undefined") return;
    const url = buildShareUrl(window.location.origin, s.id, shareState, defaults, filterIsDefault);
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      /* ignore */
    }
  };

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
            {s.kind === "match"
              ? copy("canonical.eventBanner.match")
              : `${copy("canonical.eventBanner.training")}${dayCode ? ` · ${dayCode}` : ""}`}
          </span>
          <span
            className="whitespace-nowrap text-[12.5px]"
            style={{ color: "var(--color-slate-300)" }}
          >
            {formatDate(s.dateISO)}
            <Sep />
            <span className="type-num">{s.durationMin}{copy("canonical.eventBanner.totalSuffix")}</span>
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
                className="absolute right-0 top-9 z-30 w-64 overflow-hidden rounded-md border shadow-lg"
                style={{
                  backgroundColor: "var(--color-surface-card)",
                  borderColor: "var(--color-border)",
                  color: "var(--color-text-primary)",
                }}
              >
                <MenuItem label={copy("canonical.eventBanner.exportCsv")} />
                <MenuItem label={copy("canonical.eventBanner.exportPdf")} />
                <MenuItem
                  label={copied ? "Link copied" : copy("canonical.eventBanner.copyLink")}
                  onClick={handleCopyLink}
                  icon={copied ? <Check className="h-3.5 w-3.5" /> : null}
                  data-testid="copy-link"
                />
                {!isDefault && (
                  <div
                    className="border-t px-3 py-2 text-[11.5px]"
                    style={{
                      borderColor: "var(--color-border)",
                      color: "var(--color-text-tertiary)",
                    }}
                    data-testid="share-includes-state"
                  >
                    {copy("share.includesState")}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function MenuItem({
  label,
  onClick,
  icon,
  ...rest
}: {
  label: string;
  onClick?: () => void;
  icon?: React.ReactNode;
} & React.HTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      onClick={onClick}
      className="flex w-full items-center justify-between gap-2 px-3 py-2 text-left text-[12.5px] transition-colors hover:bg-[color:var(--color-slate-100)]"
      {...rest}
    >
      <span>{label}</span>
      {icon}
    </button>
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

