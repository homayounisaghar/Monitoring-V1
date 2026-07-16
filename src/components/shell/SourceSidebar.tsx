import { useState } from "react";
import { ChevronLeft, ChevronRight, Calendar, Tag, Search, X } from "lucide-react";
import { copy } from "@/lib/copy-deck";
import { sessionLibrary, currentSession } from "@/lib/session-data";
import {
  SIDEBAR_COLLAPSED,
  SIDEBAR_EXPANDED,
  toggleSidebarCollapsed,
  useSidebarCollapsed,
} from "@/lib/sidebar-store";

export function SourceSidebar() {
  const collapsed = useSidebarCollapsed();
  const [split, setSplit] = useState<"all" | "match" | "training">("all");
  const [query, setQuery] = useState("");

  const q = query.trim().toLowerCase();
  const filtered = sessionLibrary.filter((s) => {
    if (split !== "all" && s.kind !== split) return false;
    if (q) {
      const displayName = stripDayCodePrefix(s.label, s.dayCode);
      if (!displayName.toLowerCase().includes(q)) return false;
    }
    return true;
  });

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

          {/* Session list */}
          <ul className="flex flex-col gap-0.5">
            {filtered.map((s) => {
              const selected = s.id === currentSession.id;
              const displayName = stripDayCodePrefix(s.label, s.dayCode);
              return (
                <li key={s.id}>
                  <button
                    className="flex w-full items-center gap-2 rounded px-1.5 py-1.5 text-left transition-colors"
                    style={{
                      backgroundColor: selected ? "var(--color-slate-100)" : "transparent",
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
                        {formatShort(s.dateISO)} · {s.durationMin}'
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

function formatShort(iso: string) {
  const d = new Date(iso);
  return d.toLocaleDateString("en-GB", { day: "2-digit", month: "short" });
}

function stripDayCodePrefix(label: string, dayCode: string) {
  // Escape regex specials in the day code (e.g. "MD+1", "MD-2").
  const escaped = dayCode.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return label.replace(new RegExp(`^${escaped}\\s*·\\s*`), "");
}

