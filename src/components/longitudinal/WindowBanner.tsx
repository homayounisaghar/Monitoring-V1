import { ChevronDown, Download, Share2 } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { copy, tmpl } from "@/lib/copy-deck";
import {
  SEASON_START_ISO,
  DEMO_TODAY,
} from "@/lib/demo-library";
import {
  windowComposition,
  windowFor,
  type Horizon,
  type LongiWindow,
} from "@/lib/longitudinal-data";
import { dayMonth, rangeLabel } from "@/lib/format-date";

const HORIZONS: Horizon[] = [7, 14, 28, "season"];
const DEFAULT_HORIZON: Horizon = 28;

export function WindowBanner({
  horizon,
  onHorizonChange,
  window: w,
}: {
  horizon: Horizon;
  onHorizonChange: (h: Horizon) => void;
  window: LongiWindow;
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [downloadOpen, setDownloadOpen] = useState(false);
  const [shareOpen, setShareOpen] = useState(false);

  const menuRef = useRef<HTMLDivElement>(null);
  const downloadRef = useRef<HTMLDivElement>(null);
  const shareRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!menuOpen && !downloadOpen && !shareOpen) return;
    const onDoc = (e: MouseEvent) => {
      const t = e.target as Node;
      if (menuOpen && menuRef.current && !menuRef.current.contains(t))
        setMenuOpen(false);
      if (downloadOpen && downloadRef.current && !downloadRef.current.contains(t))
        setDownloadOpen(false);
      if (shareOpen && shareRef.current && !shareRef.current.contains(t))
        setShareOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [menuOpen, downloadOpen, shareOpen]);

  const comp = windowComposition(w);
  const composition = tmpl("longi.banner.compositionTemplate", {
    days: comp.days,
    trainings: comp.nonMatchSessions,
    matches: comp.matchSessions,
  });

  const range = rangeLabel(w.startISO, w.endISO);
  const buttonLabel =
    horizon === "season"
      ? copy("longi.window.seasonButton")
      : tmpl("longi.window.buttonTemplate", { n: horizon });

  return (
    <div
      className="rounded-lg"
      style={{
        backgroundColor: "var(--color-chrome)",
        color: "var(--color-text-on-brand)",
      }}
    >
      <div className="flex h-[52px] items-center justify-between gap-6 px-5">
        <div className="flex min-w-0 items-baseline gap-x-2.5">
          <div className="relative" ref={menuRef}>
            <button
              onClick={() => setMenuOpen((o) => !o)}
              className="inline-flex items-center gap-1 rounded text-[16px] font-semibold tracking-tight outline-none transition-colors"
              aria-haspopup="menu"
              aria-expanded={menuOpen}
              style={{ color: "var(--color-text-on-brand)" }}
            >
              <span>{buttonLabel}</span>
              <ChevronDown className="h-3.5 w-3.5 opacity-80" aria-hidden />
            </button>
            {menuOpen && (
              <div
                role="menu"
                className="absolute left-0 top-9 z-40 w-64 overflow-hidden rounded-md border shadow-xl"
                style={{
                  backgroundColor: "var(--color-surface-card)",
                  borderColor: "var(--color-border)",
                  color: "var(--color-text-primary)",
                }}
              >
                {HORIZONS.map((h) => (
                  <WindowMenuItem
                    key={String(h)}
                    horizon={h}
                    active={h === horizon}
                    isDefault={h === DEFAULT_HORIZON}
                    onSelect={() => {
                      onHorizonChange(h);
                      setMenuOpen(false);
                    }}
                  />
                ))}
              </div>
            )}
          </div>

          <span
            className="whitespace-nowrap text-[12.5px]"
            style={{ color: "var(--color-slate-300)" }}
          >
            <Sep />
            {range}
            <Sep />
            <span className="type-num">{composition}</span>
          </span>
        </div>

        {/* Right — icon-only actions. Menus open, items close them, no
            further behaviour. Restored under the high-fidelity rule. */}
        <div className="flex items-center gap-1">
          <div className="relative" ref={downloadRef}>
            <IconBtn
              label="Download"
              onClick={() => {
                setDownloadOpen((o) => !o);
                setShareOpen(false);
              }}
            >
              <Download className="h-3.5 w-3.5" />
            </IconBtn>
            {downloadOpen && (
              <div
                role="menu"
                className="absolute right-0 top-9 z-30 w-56 overflow-hidden rounded-md border shadow-lg"
                style={{
                  backgroundColor: "var(--color-surface-card)",
                  borderColor: "var(--color-border)",
                  color: "var(--color-text-primary)",
                }}
              >
                <MenuItem
                  label={copy("canonical.eventBanner.exportCsv")}
                  onClick={() => setDownloadOpen(false)}
                />
                <MenuItem
                  label={copy("canonical.eventBanner.exportPdf")}
                  onClick={() => setDownloadOpen(false)}
                />
              </div>
            )}
          </div>
          <div className="relative" ref={shareRef}>
            <IconBtn
              label={copy("canonical.eventBanner.shareExport")}
              onClick={() => {
                setShareOpen((o) => !o);
                setDownloadOpen(false);
              }}
            >
              <Share2 className="h-3.5 w-3.5" />
            </IconBtn>
            {shareOpen && (
              <div
                role="menu"
                className="absolute right-0 top-9 z-30 w-56 overflow-hidden rounded-md border shadow-lg"
                style={{
                  backgroundColor: "var(--color-surface-card)",
                  borderColor: "var(--color-border)",
                  color: "var(--color-text-primary)",
                }}
              >
                <MenuItem
                  label={copy("canonical.eventBanner.copyLink")}
                  onClick={() => setShareOpen(false)}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function WindowMenuItem({
  horizon,
  active,
  isDefault,
  onSelect,
}: {
  horizon: Horizon;
  active: boolean;
  isDefault: boolean;
  onSelect: () => void;
}) {
  const label =
    horizon === 7
      ? copy("longi.window.opt.7")
      : horizon === 14
      ? copy("longi.window.opt.14")
      : horizon === 28
      ? copy("longi.window.opt.28")
      : copy("longi.window.opt.season");

  let gloss: string | null = null;
  if (horizon === "season") {
    const start = new Date(SEASON_START_ISO + "T00:00:00Z");
    const today = new Date(DEMO_TODAY + "T00:00:00Z");
    const wk = Math.max(
      1,
      Math.round((today.getTime() - start.getTime()) / (7 * 86_400_000)),
    );
    const dateStr = dayMonth(SEASON_START_ISO);
    gloss = tmpl("longi.window.seasonGlossTemplate", { date: dateStr, n: wk });
  }

  return (
    <button
      onClick={onSelect}
      className="flex w-full items-center justify-between gap-3 px-3 py-2 text-left text-[12.5px] transition-colors hover:bg-[color:var(--color-slate-100)]"
      role="menuitem"
      style={{
        color: active ? "var(--color-text-primary)" : "var(--color-text-secondary)",
        fontWeight: active ? 500 : 400,
      }}
    >
      <span>{label}</span>
      <span className="type-num text-[11px]" style={{ color: "var(--color-text-tertiary)" }}>
        {gloss ? gloss : isDefault ? copy("canonical.readingLine.default") : ""}
      </span>
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

function MenuItem({
  label,
  onClick,
}: {
  label: string;
  onClick?: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="flex w-full items-center justify-between gap-2 px-3 py-2 text-left text-[12.5px] transition-colors hover:bg-[color:var(--color-slate-100)]"
    >
      <span>{label}</span>
    </button>
  );
}

export { HORIZONS, DEFAULT_HORIZON };
export function defaultWindow(): LongiWindow {
  return windowFor(DEFAULT_HORIZON);
}
