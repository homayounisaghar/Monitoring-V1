import { copy } from "@/lib/copy-deck";
import { useState, useRef, useEffect, useMemo } from "react";
import { SlidersHorizontal, X, Search } from "lucide-react";
import {
  useSessionScope,
  currentSession,
  type Filter,
} from "@/lib/session-scope";
import {
  timeline,
  participants,
  savedSubsets,
  POSITION_LABEL,
  type ParticipationTag,
  type PositionCode,
} from "@/lib/session-data";

const PARTICIPATION: ParticipationTag[] = ["Full", "Part", "Modified", "Rehab", "Injury", "Other"];
const POSITIONS: PositionCode[] = ["GK", "DEF", "MID", "ATT"];

export function FilterCluster() {
  const { filter, setFilter, showingCount, filterIsDefault } = useSessionScope();
  const [open, setOpen] = useState(false);
  const wrapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [open]);

  const chips = useMemo(() => activeChips(filter), [filter]);
  const visibleChips = chips.slice(0, 3);
  const overflow = chips.length - visibleChips.length;

  return (
    <div className="relative flex items-center gap-2" ref={wrapRef}>
      {/* Active chips beside the button */}
      {chips.length > 0 && (
        <div className="flex items-center gap-1">
          {visibleChips.map((c) => (
            <button
              key={c.key}
              onClick={c.remove(setFilter, filter)}
              className="chip-changed inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[12px]"
            >
              <span>{c.label}</span>
              <X className="h-3 w-3" style={{ color: "var(--color-text-tertiary)" }} />
            </button>
          ))}
          {overflow > 0 && (
            <span
              className="chip-changed inline-flex items-center rounded px-1.5 py-0.5 text-[12px]"
            >
              +{overflow}
            </span>
          )}
        </div>
      )}

      <button
        onClick={() => setOpen((o) => !o)}
        className={
          "inline-flex h-8 items-center gap-1.5 rounded-md border px-2.5 text-[12.5px] transition-colors " +
          (filterIsDefault ? "" : "chip-changed")
        }
        style={
          filterIsDefault
            ? {
                borderColor: "var(--color-border)",
                backgroundColor: "var(--color-surface-card)",
                color: "var(--color-text-secondary)",
              }
            : { borderColor: "var(--color-slate-200)" }
        }
      >
        <SlidersHorizontal className="h-3.5 w-3.5" />
        <span>{copy("canonical.filter.button")}</span>
      </button>

      {open && (
        <FilterPanel
          filter={filter}
          setFilter={setFilter}
          showingCount={showingCount}
          onClose={() => setOpen(false)}
        />
      )}
    </div>
  );
}

/* ------------ Panel ------------ */

function FilterPanel({
  filter,
  setFilter,
  showingCount,
  onClose,
}: {
  filter: Filter;
  setFilter: (f: Filter) => void;
  showingCount: number;
  onClose: () => void;
}) {
  const periods = useMemo(
    () => timeline(currentSession, filter.period.granularity),
    [filter.period.granularity]
  );

  const patch = (p: Partial<Filter>) => setFilter({ ...filter, ...p });

  return (
    <div
      className="absolute right-0 top-full z-40 mt-2 w-[360px] overflow-hidden rounded-md border shadow-xl"
      style={{
        backgroundColor: "var(--color-surface-card)",
        borderColor: "var(--color-border)",
      }}
    >
      <div className="max-h-[70vh] overflow-y-auto p-4 space-y-4">
        {/* Participation */}
        <Section title={copy("canonical.filter.group.participation")}>
          <div className="flex flex-wrap gap-1">
            <ToggleAll
              active={filter.participation.size === 0}
              onClick={() => patch({ participation: new Set() })}
            />
            {PARTICIPATION.map((p) => (
              <Pill
                key={p}
                label={p}
                active={filter.participation.has(p)}
                onClick={() => {
                  const next = new Set(filter.participation);
                  next.has(p) ? next.delete(p) : next.add(p);
                  patch({ participation: next });
                }}
              />
            ))}
          </div>
        </Section>

        {/* Position */}
        <Section title={copy("canonical.filter.group.position")}>
          <div className="flex flex-wrap gap-1">
            <ToggleAll
              active={filter.positions.size === 0}
              onClick={() => patch({ positions: new Set() })}
            />
            {POSITIONS.map((p) => (
              <Pill
                key={p}
                label={POSITION_LABEL[p]}
                active={filter.positions.has(p)}
                onClick={() => {
                  const next = new Set(filter.positions);
                  next.has(p) ? next.delete(p) : next.add(p);
                  patch({ positions: next });
                }}
              />
            ))}
          </div>
        </Section>

        {/* Periods */}
        <Section title={copy("canonical.filter.group.timeWindow")}>
          <div
            className="mb-2 flex rounded-md border p-0.5"
            style={{ borderColor: "var(--color-border)" }}
          >
            {(["halves", "15min"] as const).map((g) => (
              <button
                key={g}
                onClick={() =>
                  patch({ period: { granularity: g, selected: new Set() } })
                }
                className={
                  "h-6 flex-1 rounded text-[11px] font-medium transition-colors " +
                  (filter.period.granularity === g ? "sel-active" : "sel-idle")
                }
              >
                {g === "halves" ? copy("canonical.filter.granularity.halves") : copy("canonical.filter.granularity.blocks15")}
              </button>
            ))}
          </div>
          <div className="flex flex-wrap gap-1">
            <ToggleAll
              active={filter.period.selected.size === 0}
              onClick={() =>
                patch({ period: { ...filter.period, selected: new Set() } })
              }
            />
            {periods.map((pr) => (
              <Pill
                key={pr.id}
                label={pr.label}
                active={filter.period.selected.has(pr.id)}
                onClick={() => {
                  const next = new Set(filter.period.selected);
                  next.has(pr.id) ? next.delete(pr.id) : next.add(pr.id);
                  patch({ period: { ...filter.period, selected: next } });
                }}
              />
            ))}
          </div>
        </Section>

        {/* Athletes */}
        <Section title={copy("canonical.filter.group.athletes")}>
          <AthletePicker
            selected={filter.athletes}
            onChange={(next) => patch({ athletes: next })}
          />
          <div className="mt-2 flex gap-1">
            <QuickAdd
              label={copy("canonical.filter.quickAdd.rtp")}
              onClick={() => {
                const next = new Set(filter.athletes);
                savedSubsets.rtp.forEach((id) => next.add(id));
                patch({ athletes: next });
              }}
            />
            <QuickAdd
              label={copy("canonical.filter.quickAdd.setpiece")}
              onClick={() => {
                const next = new Set(filter.athletes);
                savedSubsets.setpiece.forEach((id) => next.add(id));
                patch({ athletes: next });
              }}
            />
          </div>
        </Section>
      </div>

      {/* Footer */}
      <div
        className="flex items-center justify-between border-t px-4 py-2.5"
        style={{
          borderColor: "var(--color-border)",
          backgroundColor: "var(--color-slate-50)",
        }}
      >
        <span className="text-[12px]" style={{ color: "var(--color-text-secondary)" }}>
          {copy("canonical.filter.showingPrefix")} <span className="type-num font-semibold" style={{ color: "var(--color-text-primary)" }}>{showingCount}</span> {copy("canonical.filter.showingConnector")} {participants.length}
        </span>
        <div className="flex items-center gap-2">
          {!isFilterDefault(filter) && (
            <button
              onClick={() =>
                setFilter({
                  participation: new Set(),
                  positions: new Set(),
                  period: { granularity: filter.period.granularity, selected: new Set() },
                  athletes: new Set(),
                })
              }
              className="text-[12px] transition-colors hover:underline"
              style={{ color: "var(--color-text-secondary)" }}
            >
              {copy("control.clearAll")}
            </button>
          )}
          <button
            onClick={onClose}
            className="rounded px-3 py-1 text-[12px] font-medium sel-active"
          >
            {copy("canonical.filter.done")}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ------------ Sub-parts ------------ */

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <div
        className="type-label mb-1.5"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        {title}
      </div>
      {children}
    </div>
  );
}

function Pill({
  label, active, onClick,
}: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={
        "h-6 rounded-md border px-2 text-[11.5px] transition-colors " +
        (active ? "sel-active" : "sel-idle")
      }
      style={{ borderColor: active ? "transparent" : "var(--color-border)" }}
    >
      {label}
    </button>
  );
}

function ToggleAll({ active, onClick }: { active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={
        "h-6 rounded-md border px-2 text-[11.5px] transition-colors " +
        (active ? "sel-active" : "sel-idle")
      }
      style={{ borderColor: active ? "transparent" : "var(--color-border)" }}
    >
      {copy("canonical.filter.all")}
    </button>
  );
}

function QuickAdd({ label, onClick }: { label: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="rounded-md border px-2 py-1 text-[11.5px] transition-colors hover:bg-[color:var(--color-slate-100)]"
      style={{
        borderColor: "var(--color-border)",
        color: "var(--color-text-secondary)",
      }}
    >
      {label}
    </button>
  );
}

function AthletePicker({
  selected,
  onChange,
}: {
  selected: Set<string>;
  onChange: (next: Set<string>) => void;
}) {
  const [q, setQ] = useState("");
  const [focus, setFocus] = useState(false);
  const matches = useMemo(() => {
    if (!q) return [];
    const needle = q.toLowerCase();
    return participants
      .filter((a) => a.name.toLowerCase().includes(needle) && !selected.has(a.id))
      .slice(0, 6);
  }, [q, selected]);

  return (
    <div className="space-y-1.5">
      <div
        className="flex h-8 items-center gap-1.5 rounded-md border px-2"
        style={{
          borderColor: "var(--color-border)",
          backgroundColor: "var(--color-surface-card)",
        }}
      >
        <Search className="h-3 w-3" style={{ color: "var(--color-text-tertiary)" }} />
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onFocus={() => setFocus(true)}
          onBlur={() => setTimeout(() => setFocus(false), 120)}
          placeholder={copy("canonical.filter.findAthletes")}
          className="w-full bg-transparent text-[12px] outline-none"
          style={{ color: "var(--color-text-primary)" }}
        />
      </div>

      {focus && matches.length > 0 && (
        <ul
          className="rounded-md border p-1"
          style={{
            borderColor: "var(--color-border)",
            backgroundColor: "var(--color-surface-card)",
          }}
        >
          {matches.map((a) => (
            <li key={a.id}>
              <button
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => {
                  const next = new Set(selected);
                  next.add(a.id);
                  onChange(next);
                  setQ("");
                }}
                className="flex w-full items-center justify-between rounded px-2 py-1 text-left text-[12px] transition-colors hover:bg-[color:var(--color-slate-100)]"
                style={{ color: "var(--color-text-primary)" }}
              >
                <span>{a.name}</span>
                <span className="type-microcaps" style={{ color: "var(--color-text-tertiary)" }}>
                  {a.posDetail}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}

      {selected.size > 0 && (
        <div className="flex flex-wrap gap-1">
          {[...selected].map((id) => {
            const a = participants.find((x) => x.id === id);
            if (!a) return null;
            return (
              <button
                key={id}
                onClick={() => {
                  const next = new Set(selected);
                  next.delete(id);
                  onChange(next);
                }}
                className="chip-changed inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[11.5px]"
              >
                <span>{a.name}</span>
                <X className="h-3 w-3" style={{ color: "var(--color-text-tertiary)" }} />
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* ------------ Chip rendering + filter defaults ------------ */

function isFilterDefault(f: Filter) {
  return (
    f.participation.size === 0 &&
    f.positions.size === 0 &&
    f.period.selected.size === 0 &&
    f.athletes.size === 0
  );
}

type ChipDescriptor = {
  key: string;
  label: string;
  remove: (setFilter: (f: Filter) => void, current: Filter) => () => void;
};

function activeChips(f: Filter): ChipDescriptor[] {
  const chips: ChipDescriptor[] = [];
  f.positions.forEach((p) =>
    chips.push({
      key: `pos:${p}`,
      label: POSITION_LABEL[p],
      remove: (setFilter, current) => () => {
        const next = new Set(current.positions);
        next.delete(p);
        setFilter({ ...current, positions: next });
      },
    })
  );
  f.participation.forEach((p) =>
    chips.push({
      key: `part:${p}`,
      label: p,
      remove: (setFilter, current) => () => {
        const next = new Set(current.participation);
        next.delete(p);
        setFilter({ ...current, participation: next });
      },
    })
  );
  f.period.selected.forEach((id) => {
    const opts = timeline(currentSession, f.period.granularity);
    const opt = opts.find((o) => o.id === id);
    chips.push({
      key: `per:${id}`,
      label: opt?.label ?? id,
      remove: (setFilter, current) => () => {
        const next = new Set(current.period.selected);
        next.delete(id);
        setFilter({ ...current, period: { ...current.period, selected: next } });
      },
    });
  });
  if (f.athletes.size > 0) {
    chips.push({
      key: "ath",
      label: `${f.athletes.size} ${f.athletes.size > 1 ? copy("canonical.filter.athletesChip.many") : copy("canonical.filter.athletesChip.one")}`,
      remove: (setFilter, current) => () =>
        setFilter({ ...current, athletes: new Set() }),
    });
  }
  return chips;
}
