import { useMemo, useState } from "react";
import { ChevronLeft, ChevronRight, Calendar, Tag, Search, X } from "lucide-react";
import { copy, tmpl } from "@/lib/copy-deck";
import { currentSession } from "@/lib/session-data";
import { demoSessions, DEMO_TODAY, type DemoSession } from "@/lib/demo-library";
import { dayMonth2 } from "@/lib/format-date";
import {
  SIDEBAR_COLLAPSED,
  SIDEBAR_EXPANDED,
  toggleSidebarCollapsed,
  useSidebarCollapsed,
} from "@/lib/sidebar-store";

export type SidebarScope = {
  startISO: string;
  endISO: string;
  horizonDays: number; // for the "{d}-day window" phrasing
};

type SourceSidebarProps = {
  scope?: SidebarScope;
  focusSessionId?: string;
  onFocusSession?: (id: string) => void;
  showOutOfWindow?: boolean;
};

type SidebarRow = {
  id: string;
  kind: "match" | "training";
  label: string;
  dayCode: string;
  dateISO: string;
  durationMin: number;
  unconfirmed: boolean;
  inWindow: boolean;
};

function daysBetween(aIso: string, bIso: string): number {
  const a = new Date(aIso + "T00:00:00Z").getTime();
  const b = new Date(bIso + "T00:00:00Z").getTime();
  return Math.round((a - b) / 86_400_000);
}

function toRow(s: DemoSession, inWindow: boolean): SidebarRow {
  const kind: "match" | "training" = s.type === "match" ? "match" : "training";
  const label = s.type === "match" && s.opponent ? `vs ${s.opponent}` : s.name;
  return {
    id: s.id,
    kind,
    label,
    dayCode: s.dayCode,
    dateISO: s.dateISO,
    durationMin: s.durationMin,
    unconfirmed: Boolean(s.unconfirmed),
    inWindow,
  };
}

export function SourceSidebar(props: SourceSidebarProps = {}) {
  const { scope, focusSessionId, onFocusSession, showOutOfWindow = false } = props;
  const collapsed = useSidebarCollapsed();
  const [split, setSplit] = useState<"all" | "match" | "training">("all");
  const [query, setQuery] = useState("");

  // Row source: scoped (window + optional out-of-window tail) or the shipped
  // 30-day default when no scope is passed.
  const sessionLibrary = useMemo<SidebarRow[]>(() => {
    const cmp = (a: SidebarRow, b: SidebarRow) =>
      a.dateISO === b.dateISO
        ? b.id.localeCompare(a.id)
        : a.dateISO < b.dateISO ? 1 : -1;

    if (!scope) {
      return demoSessions
        .filter((s) => {
          const age = daysBetween(DEMO_TODAY, s.dateISO);
          return age >= 0 && age <= 30;
        })
        .map((s) => toRow(s, true))
        .sort(cmp);
    }

    const inWin = demoSessions
      .filter((s) => s.dateISO >= scope.startISO && s.dateISO <= scope.endISO)
      .map((s) => toRow(s, true))
      .sort(cmp);
    if (!showOutOfWindow) return inWin;

    // Muted tail: sessions before the window's start, most-recent-first, capped.
    const OUT_CAP = 12;
    const out = demoSessions
      .filter((s) => s.dateISO < scope.startISO)
      .map((s) => toRow(s, false))
      .sort(cmp)
      .slice(0, OUT_CAP);
    return [...inWin, ...out];
  }, [scope, showOutOfWindow]);

  const q = query.trim().toLowerCase();
  const filtered = sessionLibrary.filter((s) => {
    if (split !== "all" && s.kind !== split) return false;
    if (q) {
      const displayName = stripDayCodePrefix(s.label, s.dayCode);
      if (!displayName.toLowerCase().includes(q)) return false;
    }
    return true;
  });

  // Sub-line — chosen from deck by presence of scope; component owns the copy.
  const inWindowCount = sessionLibrary.filter((s) => s.inWindow).length;
  const OVERFLOW_CAP = 15;
  const overflowN = scope ? Math.max(0, inWindowCount - OVERFLOW_CAP) : 0;
  let subline: string | null = null;
  if (scope) {
    // "24 sessions in the window" total is the visible-max: sessions in a 28-day
    // window ending on the same day. When the current horizon equals that max,
    // it prints "all N"; a shorter horizon prints "N of M".
    const endMs = new Date(scope.endISO + "T00:00:00Z").getTime();
    const max28StartMs = endMs - 27 * 86_400_000;
    const max28Start = new Date(max28StartMs).toISOString().slice(0, 10);
    const max28Count = demoSessions.filter(
      (s) => s.dateISO >= max28Start && s.dateISO <= scope.endISO,
    ).length;
    if (inWindowCount === max28Count) {
      subline = tmpl("sidebar.subline.allInWindowTemplate", { n: inWindowCount });
    } else {
      subline = tmpl("sidebar.subline.partialTemplate", {
        n: inWindowCount,
        m: max28Count,
        d: scope.horizonDays,
      });
    }
  }

  const selectedId = focusSessionId ?? currentSession.id;
  const handleClick = (id: string) => {
    if (onFocusSession) onFocusSession(id);
  };



  return (
    <aside
      className="sticky top-12 h-[calc(100vh-3rem)] shrink-0 border-r transition-[width] duration-200"
      style={{
        width: collapsed ? SIDEBAR_COLLAPSED : SIDEBAR_EXPANDED,
        backgroundColor: "var(--color-surface-card)",
        borderColor: "var(--color-border)",
      }}
    >
      <div className="flex h-10 items-center justify-between px-2">
        {!collapsed && (
          <span
            className="type-microcaps px-1.5"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {copy("sidebar.header")}
          </span>
        )}
        <button
          onClick={() => toggleSidebarCollapsed()}
          className="ml-auto grid h-7 w-7 place-items-center rounded transition-colors hover:bg-[color:var(--color-slate-100)]"
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? (
            <ChevronRight className="h-3.5 w-3.5" style={{ color: "var(--color-text-secondary)" }} />
          ) : (
            <ChevronLeft className="h-3.5 w-3.5" style={{ color: "var(--color-text-secondary)" }} />
          )}
        </button>
      </div>

      {collapsed ? (
        <CollapsedRail />
      ) : (
        <div className="flex flex-col gap-3 px-2 pb-4">
          {/* Filters */}
          <div className="flex flex-col gap-1.5 px-1.5">
            <div
              className="flex h-7 items-center gap-1.5 rounded-md border px-1.5"
              style={{
                borderColor: "var(--color-border)",
                backgroundColor: "var(--color-canvas)",
              }}
            >
              <Search className="h-3 w-3 shrink-0" style={{ color: "var(--color-text-tertiary)" }} aria-hidden />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={copy("sidebar.searchPlaceholder")}
                aria-label={copy("sidebar.searchPlaceholder")}
                className="w-full bg-transparent text-[12px] outline-none placeholder:opacity-70"
                style={{ color: "var(--color-text-primary)" }}
              />
              {query && (
                <button
                  onClick={() => setQuery("")}
                  aria-label={copy("sidebar.searchClear")}
                  title={copy("sidebar.searchClear")}
                  className="grid h-4 w-4 shrink-0 place-items-center rounded transition-colors hover:bg-[color:var(--color-slate-200)]"
                  style={{ color: "var(--color-text-tertiary)" }}
                >
                  <X className="h-3 w-3" />
                </button>
              )}
            </div>
            <button
              className="flex h-7 items-center gap-1.5 rounded px-1.5 text-[12px] transition-colors hover:bg-[color:var(--color-slate-100)]"
              style={{ color: "var(--color-text-secondary)" }}
            >
              <Calendar className="h-3 w-3" />
              <span>Last 30 days</span>
            </button>
            <button
              className="flex h-7 items-center gap-1.5 rounded px-1.5 text-[12px] transition-colors hover:bg-[color:var(--color-slate-100)]"
              style={{ color: "var(--color-text-secondary)" }}
            >
              <Tag className="h-3 w-3" />
              <span>All tags</span>
            </button>
          </div>


          {/* Match / Training split — segmented */}
          <div
            className="mx-1.5 flex rounded-md border p-0.5"
            style={{ borderColor: "var(--color-border)" }}
          >
            {(["all", "match", "training"] as const).map((opt) => (
              <button
                key={opt}
                onClick={() => setSplit(opt)}
                className={
                  "h-6 flex-1 rounded text-[11px] font-medium capitalize transition-colors " +
                  (split === opt ? "sel-active" : "sel-idle")
                }
              >
                {opt}
              </button>
            ))}
          </div>

          {/* Sub-line — scoped windows only */}
          {subline && (
            <div
              className="px-2.5 text-[11px]"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              {subline}
            </div>
          )}

          {/* Session list */}
          <ul className="flex flex-col gap-0.5">
            {filtered.map((s) => {
              const selected = s.id === selectedId;
              const displayName = stripDayCodePrefix(s.label, s.dayCode);
              const muted = !s.inWindow;
              return (
                <li key={s.id}>
                  <button
                    onClick={() => handleClick(s.id)}
                    className="flex w-full items-center gap-2 rounded px-1.5 py-1.5 text-left transition-colors"
                    style={{
                      backgroundColor: selected ? "var(--color-slate-100)" : "transparent",
                      opacity: muted ? 0.5 : 1,
                    }}
                  >
                    <span className="flex min-w-0 flex-1 flex-col">
                      <span
                        className="truncate text-[12.5px] font-medium"
                        style={{
                          color: selected ? "var(--color-text-primary)" : "var(--color-text-secondary)",
                        }}
                      >
                        {displayName}
                      </span>
                      <span
                        className="type-num text-[10.5px]"
                        style={{ color: "var(--color-text-tertiary)" }}
                      >
                        {dayMonth2(s.dateISO)} · {s.durationMin}'
                        {s.unconfirmed && (
                          <span className="ml-1">{copy("sidebar.rowUnconfirmedSuffix")}</span>
                        )}
                      </span>
                    </span>
                    <span
                      className="type-num shrink-0 rounded-sm px-1.5 py-0.5 text-[10px] font-semibold"
                      style={{
                        backgroundColor: "var(--color-slate-100)",
                        color: "var(--color-text-secondary)",
                        border: "1px solid var(--color-border)",
                      }}
                      aria-label={`Day code ${s.dayCode}`}
                      title={s.dayCode}
                    >
                      {s.dayCode}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
          {overflowN > 0 && (
            <div
              className="px-2.5 py-1 text-[11px]"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              {tmpl("sidebar.overflowTemplate", { n: overflowN })}
            </div>
          )}
          {filtered.length === 0 && (
            <div
              className="px-2.5 py-2 text-[12px]"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              {copy("sidebar.searchEmpty")}
            </div>
          )}

        </div>
      )}
    </aside>
  );
}


function CollapsedRail() {
  return (
    <div className="flex flex-col items-center gap-2 pt-1">
      {/* Only the selected identity — never library totals */}
      <span
        className="h-1.5 w-1.5 rounded-full"
        style={{ backgroundColor: "var(--color-brand)" }}
        title="Current session"
        aria-hidden
      />
      <span
        className="type-microcaps rotate-180 [writing-mode:vertical-rl]"
        style={{ color: "var(--color-text-secondary)" }}
      >
        {currentSession.label}
      </span>
    </div>
  );
}


function stripDayCodePrefix(label: string, dayCode: string) {
  // Escape regex specials in the day code (e.g. "MD+1", "MD-2").
  const escaped = dayCode.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return label.replace(new RegExp(`^${escaped}\\s*·\\s*`), "");
}

