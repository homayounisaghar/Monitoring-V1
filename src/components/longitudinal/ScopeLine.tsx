/**
 * Longitudinal — scope line.
 *
 * High-fidelity prototype: choosing an option moves the check AND the
 * chip's label; the Summary tick and the Days 100-line follow the
 * Benchmark chip, the Athletes basis line follows the Reference chip.
 * Numbers do not recompute — that is the honesty floor. Non-default
 * labels take the slate tint, chip and echoing ticks alike; a non-default
 * chip carries a dismissible × that resets to default.
 *
 * Benchmark set is Longitudinal-specific (one family — the squad's own
 * history): typical_daytype (default), previous_window, season. The
 * match-scoped options (typical_match, last_match, same_opponent) have
 * no referent for a multi-day window and live only on Session.
 *
 * Reference set: own_typical (default), previous_window, season,
 * positional, cohort. Hairline separator after "season".
 *
 * Filter categories in fixed order: Participation, Positions, Athletes,
 * Session-type. Options render and check; Apply produces dismissible chips.
 * `positional norm` withholds below the cohort floor (default 4) — data
 * behaviour, due when scoping is wired; the option renders normally now.
 */
import { ChevronDown, Filter as FilterIcon, Check, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { copy, tmpl } from "@/lib/copy-deck";
import { LegendPopover } from "./LegendPopover";
import type { LongiWindow, Horizon } from "@/lib/longitudinal-data";
import {
  PARTICIPATION_TAGS,
  TAG_STYLE,
} from "@/lib/participation-style";
import { POSITION_LABEL, type PositionCode, type ParticipationTag } from "@/lib/session-data";
import { demoAthletes } from "@/lib/demo-library";

/* ─────────────────── option sets ─────────────────── */

export type BenchKind =
  | "typical_daytype"
  | "previous_window"
  | "season";

export type RefKind =
  | "own_typical"
  | "previous_window"
  | "season"
  | "positional"
  | "cohort";

export const BENCH_ORDER: BenchKind[] = [
  "typical_daytype",
  "previous_window",
  "season",
];

export const REF_ORDER: RefKind[] = [
  "own_typical",
  "previous_window",
  "season",
  "positional",
  "cohort",
];

/** Reference options with hairline separators after this family. */
const REF_FAMILY_END: ReadonlySet<RefKind> = new Set(["season"]);

export const DEFAULT_BENCH: BenchKind = "typical_daytype";
export const DEFAULT_REF: RefKind = "own_typical";

export function benchLabel(k: BenchKind, horizon: Horizon): string {
  if (k === "previous_window") {
    return horizon === "season"
      ? copy("longi.bench.opt.previous_period")
      : tmpl("longi.bench.opt.previous_window", { n: horizon });
  }
  return copy(`longi.bench.opt.${k}`);
}
export function refLabel(k: RefKind, horizon: Horizon): string {
  if (k === "previous_window") {
    return horizon === "season"
      ? copy("longi.ref.opt.previous_period")
      : tmpl("longi.ref.opt.previous_window", { n: horizon });
  }
  return copy(`longi.ref.opt.${k}`);
}
function benchGloss(k: BenchKind, horizon: Horizon): string {
  if (k === "previous_window") {
    return horizon === "season"
      ? copy("longi.bench.gloss.previous_period")
      : tmpl("longi.bench.gloss.previous_window", { n: horizon });
  }
  return copy(`longi.bench.gloss.${k}`);
}
function refGloss(k: RefKind, horizon: Horizon): string {
  if (k === "previous_window") {
    return horizon === "season"
      ? copy("longi.ref.gloss.previous_period")
      : tmpl("longi.ref.gloss.previous_window", { n: horizon });
  }
  return copy(`longi.ref.gloss.${k}`);
}


/* ─────────────────── filter state (demo-local) ─────────────────── */

type SessionTypeOpt = "matches" | "training";
type FilterState = {
  participation: Set<ParticipationTag>;
  positions: Set<PositionCode>;
  athletes: Set<string>;
  sessionType: Set<SessionTypeOpt>;
};

function emptyFilter(): FilterState {
  return {
    participation: new Set(),
    positions: new Set(),
    athletes: new Set(),
    sessionType: new Set(),
  };
}

function cloneFilter(f: FilterState): FilterState {
  return {
    participation: new Set(f.participation),
    positions: new Set(f.positions),
    athletes: new Set(f.athletes),
    sessionType: new Set(f.sessionType),
  };
}

function isEmpty(f: FilterState): boolean {
  return (
    f.participation.size === 0 &&
    f.positions.size === 0 &&
    f.athletes.size === 0 &&
    f.sessionType.size === 0
  );
}

/* ─────────────────── section ─────────────────── */

export function ScopeLine({
  window: w,
  horizon,
  benchKind,
  onBenchChange,
  refKind,
  onRefChange,
}: {
  window: LongiWindow;
  horizon: Horizon;
  benchKind: BenchKind;
  onBenchChange: (k: BenchKind) => void;
  refKind: RefKind;
  onRefChange: (k: RefKind) => void;
}) {
  const [applied, setApplied] = useState<FilterState>(emptyFilter());

  const dismiss = (mut: (f: FilterState) => void) =>
    setApplied((s) => {
      const next = cloneFilter(s);
      mut(next);
      return next;
    });

  return (
    <div className="flex min-w-0 flex-1 flex-wrap items-center gap-2">
      <span className="text-[12.5px]" style={{ color: "var(--color-text-secondary)" }}>
        {copy("longi.scope.squadPrefix")}
      </span>
      <BenchmarkChip active={benchKind} onSelect={onBenchChange} horizon={horizon} />
      <Sep />
      <span className="text-[12.5px]" style={{ color: "var(--color-text-secondary)" }}>
        {copy("longi.scope.athletePrefix")}
      </span>
      <ReferenceChip active={refKind} onSelect={onRefChange} horizon={horizon} />

      {/* Applied filter chips */}
      {[...applied.participation].map((p) => (
        <AppliedChip
          key={`p-${p}`}
          label={p}
          onDismiss={() => dismiss((f) => f.participation.delete(p))}
        />
      ))}
      {[...applied.positions].map((p) => (
        <AppliedChip
          key={`pos-${p}`}
          label={POSITION_LABEL[p]}
          onDismiss={() => dismiss((f) => f.positions.delete(p))}
        />
      ))}
      {[...applied.athletes].map((id) => {
        const a = demoAthletes.find((x) => x.id === id);
        return (
          <AppliedChip
            key={`a-${id}`}
            label={a ? a.name : id}
            onDismiss={() => dismiss((f) => f.athletes.delete(id))}
          />
        );
      })}
      {[...applied.sessionType].map((opt) => (
        <AppliedChip
          key={`stype-${opt}`}
          label={
            opt === "matches"
              ? copy("longi.filter.opt.matches")
              : copy("longi.filter.opt.training")
          }
          onDismiss={() => dismiss((f) => f.sessionType.delete(opt))}
        />
      ))}

      <div className="ml-auto flex items-center gap-3">
        <LegendPopover window={w} />
        <FilterButton applied={applied} onApply={setApplied} />
      </div>
    </div>
  );
}

/* ─────────────────── chips ─────────────────── */

function Sep() {
  return (
    <span
      aria-hidden
      className="text-[12.5px]"
      style={{ color: "var(--color-text-tertiary)" }}
    >
      {copy("longi.scope.separator")}
    </span>
  );
}

function BenchmarkChip({
  active,
  onSelect,
  horizon,
}: {
  active: BenchKind;
  onSelect: (k: BenchKind) => void;
  horizon: Horizon;
}) {
  const [open, setOpen] = useState(false);
  const wrapRef = useOutsideClose(open, () => setOpen(false));
  const isDefault = active === DEFAULT_BENCH;

  return (
    <div className="relative" ref={wrapRef}>
      <ChipButton
        open={open}
        onClick={() => setOpen((o) => !o)}
        changed={!isDefault}
        onReset={!isDefault ? () => onSelect(DEFAULT_BENCH) : undefined}
      >
        {benchLabel(active, horizon)}
      </ChipButton>
      {open && (
        <Popover>
          <MenuHead title={copy("longi.scope.benchmarkMenuTitle")} />
          {BENCH_ORDER.map((k) => (
            <OptionRow
              key={k}
              label={benchLabel(k, horizon)}
              gloss={benchGloss(k, horizon)}
              checked={k === active}
              isDefault={k === DEFAULT_BENCH}
              onClick={() => {
                onSelect(k);
                setOpen(false);
              }}
            />
          ))}
          <FootGloss text={copy("longi.scope.benchmarkGloss")} />
        </Popover>
      )}
    </div>
  );
}

function ReferenceChip({
  active,
  onSelect,
  horizon,
}: {
  active: RefKind;
  onSelect: (k: RefKind) => void;
  horizon: Horizon;
}) {
  const [open, setOpen] = useState(false);
  const wrapRef = useOutsideClose(open, () => setOpen(false));
  const isDefault = active === DEFAULT_REF;

  return (
    <div className="relative" ref={wrapRef}>
      <ChipButton
        open={open}
        onClick={() => setOpen((o) => !o)}
        changed={!isDefault}
        onReset={!isDefault ? () => onSelect(DEFAULT_REF) : undefined}
      >
        {refLabel(active, horizon)}
      </ChipButton>
      {open && (
        <Popover>
          <MenuHead title={copy("longi.scope.referenceMenuTitle")} />
          {REF_ORDER.map((k, i) => (
            <div key={k}>
              <OptionRow
                label={refLabel(k, horizon)}
                gloss={refGloss(k, horizon)}
                checked={k === active}
                isDefault={k === DEFAULT_REF}
                onClick={() => {
                  onSelect(k);
                  setOpen(false);
                }}
              />
              {REF_FAMILY_END.has(k) && i < REF_ORDER.length - 1 && (
                <div
                  aria-hidden
                  className="mx-2 my-1 h-px"
                  style={{ backgroundColor: "var(--color-border)" }}
                />
              )}
            </div>
          ))}
        </Popover>
      )}
    </div>
  );
}

function ChipButton({
  children,
  open,
  onClick,
  changed,
  onReset,
}: {
  children: React.ReactNode;
  open: boolean;
  onClick: () => void;
  changed: boolean;
  onReset?: () => void;
}) {
  return (
    <span
      className={
        "inline-flex items-center rounded-full border " +
        (changed ? "chip-changed" : "hover:bg-[color:var(--color-slate-50)]")
      }
      style={
        changed
          ? undefined
          : {
              borderColor: "var(--color-border)",
              color: "var(--color-text-secondary)",
              backgroundColor: "var(--color-surface-card)",
            }
      }
    >
      <button
        onClick={onClick}
        aria-haspopup="menu"
        aria-expanded={open}
        className="inline-flex items-center gap-1 px-2.5 py-1 text-[12.5px]"
        style={{ color: "inherit" }}
      >
        <span>{children}</span>
        <ChevronDown className="h-3 w-3 opacity-70" aria-hidden />
      </button>
      {onReset && (
        <button
          type="button"
          onClick={onReset}
          aria-label={copy("longi.filter.chipDismissAria")}
          className="grid h-5 w-5 place-items-center rounded-full pr-1 transition-colors hover:bg-[color:var(--color-slate-100)]"
          style={{ color: "inherit" }}
        >
          <X className="h-3 w-3" />
        </button>
      )}
    </span>
  );
}

function AppliedChip({ label, onDismiss }: { label: string; onDismiss: () => void }) {
  return (
    <span
      className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[12px]"
      style={{
        borderColor: "var(--color-border)",
        backgroundColor: "var(--color-slate-50)",
        color: "var(--color-text-primary)",
      }}
    >
      <span>{label}</span>
      <button
        type="button"
        onClick={onDismiss}
        aria-label={copy("longi.filter.chipDismissAria")}
        className="grid h-4 w-4 place-items-center rounded-full transition-colors hover:bg-[color:var(--color-slate-100)]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        <X className="h-3 w-3" />
      </button>
    </span>
  );
}

/* ─────────────────── filter button + panel ─────────────────── */

function FilterButton({
  applied,
  onApply,
}: {
  applied: FilterState;
  onApply: (f: FilterState) => void;
}) {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState<FilterState>(() => cloneFilter(applied));
  const wrapRef = useOutsideClose(open, () => setOpen(false));

  const activeCount =
    applied.participation.size +
    applied.positions.size +
    applied.athletes.size +
    applied.sessionType.size;

  const toggle = <K,>(set: Set<K>, opt: K): Set<K> => {
    const n = new Set(set);
    if (n.has(opt)) n.delete(opt);
    else n.add(opt);
    return n;
  };

  const positionCodes: PositionCode[] = ["GK", "DEF", "MID", "ATT"];

  return (
    <div className="relative" ref={wrapRef}>
      <button
        onClick={() => {
          setDraft(cloneFilter(applied));
          setOpen((o) => !o);
        }}
        aria-haspopup="dialog"
        aria-expanded={open}
        className="inline-flex items-center gap-1.5 rounded border px-2 py-1 text-[12px] transition-colors hover:bg-[color:var(--color-slate-50)]"
        style={{
          borderColor: "var(--color-border)",
          color: "var(--color-text-secondary)",
          backgroundColor: "var(--color-surface-card)",
        }}
      >
        <FilterIcon className="h-3.5 w-3.5" aria-hidden />
        <span>{copy("control.filter")}</span>
        {activeCount > 0 && (
          <span
            className="type-num ml-0.5 rounded-full px-1.5 text-[10.5px]"
            style={{
              backgroundColor: "var(--color-slate-100)",
              color: "var(--color-text-primary)",
            }}
          >
            {activeCount}
          </span>
        )}
      </button>
      {open && (
        <div
          role="dialog"
          className="absolute right-0 top-full z-40 mt-2 w-[320px] max-h-[70vh] overflow-y-auto rounded-md border shadow-xl"
          style={{
            backgroundColor: "var(--color-surface-card)",
            borderColor: "var(--color-border)",
            color: "var(--color-text-primary)",
          }}
        >
          <div
            className="flex items-center justify-between px-3 py-2 type-microcaps"
            style={{
              color: "var(--color-text-secondary)",
              borderBottom: "1px solid var(--color-border)",
            }}
          >
            <span>{copy("longi.filter.title")}</span>
          </div>

          {/* Participation */}
          <FilterGroup title={copy("longi.filter.group.participation")}>
            {PARTICIPATION_TAGS.map((t) => (
              <CheckRow
                key={t}
                label={t}
                swatch={TAG_STYLE[t]}
                checked={draft.participation.has(t)}
                onClick={() =>
                  setDraft((s) => ({ ...s, participation: toggle(s.participation, t) }))
                }
              />
            ))}
          </FilterGroup>

          {/* Positions */}
          <FilterGroup title={copy("longi.filter.group.positions")}>
            {positionCodes.map((p) => (
              <CheckRow
                key={p}
                label={POSITION_LABEL[p]}
                checked={draft.positions.has(p)}
                onClick={() =>
                  setDraft((s) => ({ ...s, positions: toggle(s.positions, p) }))
                }
              />
            ))}
          </FilterGroup>

          {/* Athletes */}
          <FilterGroup title={copy("longi.filter.group.athletes")}>
            <div className="max-h-40 overflow-y-auto">
              {demoAthletes.map((a) => (
                <CheckRow
                  key={a.id}
                  label={a.name}
                  checked={draft.athletes.has(a.id)}
                  onClick={() =>
                    setDraft((s) => ({ ...s, athletes: toggle(s.athletes, a.id) }))
                  }
                />
              ))}
            </div>
          </FilterGroup>

          {/* Session type — last, per workstream doc */}
          <FilterGroup title={copy("longi.filter.group.sessionType")}>
            <CheckRow
              label={copy("longi.filter.opt.matches")}
              checked={draft.sessionType.has("matches")}
              onClick={() =>
                setDraft((s) => ({ ...s, sessionType: toggle(s.sessionType, "matches") }))
              }
            />
            <CheckRow
              label={copy("longi.filter.opt.training")}
              checked={draft.sessionType.has("training")}
              onClick={() =>
                setDraft((s) => ({ ...s, sessionType: toggle(s.sessionType, "training") }))
              }
            />
          </FilterGroup>

          <div
            className="flex items-center justify-between gap-2 border-t px-3 py-2"
            style={{ borderColor: "var(--color-border)" }}
          >
            <button
              onClick={() => setDraft(emptyFilter())}
              className="text-[12px] transition-colors hover:underline"
              style={{ color: "var(--color-text-secondary)" }}
            >
              {copy("control.clearAll")}
            </button>
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setOpen(false)}
                className="rounded px-2 py-1 text-[12px] transition-colors hover:bg-[color:var(--color-slate-100)]"
                style={{ color: "var(--color-text-secondary)" }}
              >
                {copy("control.cancel")}
              </button>
              <button
                onClick={() => {
                  onApply(cloneFilter(draft));
                  setOpen(false);
                }}
                className="rounded px-2.5 py-1 text-[12px] transition-colors"
                style={{
                  backgroundColor: "var(--color-chrome)",
                  color: "var(--color-text-on-brand)",
                }}
              >
                {copy("control.apply")}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function FilterGroup({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="border-t px-3 py-2" style={{ borderColor: "var(--color-border)" }}>
      <div
        className="type-microcaps mb-1.5"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        {title}
      </div>
      <div className="flex flex-col">{children}</div>
    </div>
  );
}

/* ─────────────────── shared popover shells ─────────────────── */

function Popover({ children }: { children: React.ReactNode }) {
  return (
    <div
      role="menu"
      className="absolute left-0 top-full z-40 mt-2 w-[320px] overflow-hidden rounded-md border shadow-xl"
      style={{
        backgroundColor: "var(--color-surface-card)",
        borderColor: "var(--color-border)",
        color: "var(--color-text-primary)",
      }}
    >
      {children}
    </div>
  );
}

function MenuHead({ title }: { title: string }) {
  return (
    <div
      className="type-microcaps px-3 py-2"
      style={{
        color: "var(--color-text-secondary)",
        borderBottom: "1px solid var(--color-border)",
      }}
    >
      {title}
    </div>
  );
}

function OptionRow({
  label,
  gloss,
  checked,
  isDefault,
  onClick,
}: {
  label: string;
  gloss?: string;
  checked: boolean;
  isDefault?: boolean;
  onClick: () => void;
}) {
  return (
    <button
      role="menuitemradio"
      aria-checked={checked}
      onClick={onClick}
      className="block w-full px-3 py-2 text-left transition-colors hover:bg-[color:var(--color-slate-100)]"
    >
      <span className="flex items-center justify-between gap-3">
        <span
          className="text-[12.5px]"
          style={{
            color: checked ? "var(--color-text-primary)" : "var(--color-text-secondary)",
            fontWeight: checked ? 500 : 400,
          }}
        >
          {label}
        </span>
        <span className="flex items-center gap-2">
          {isDefault && (
            <span
              className="type-label"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              {copy("canonical.readingLine.default")}
            </span>
          )}
          {checked && <Check className="h-3.5 w-3.5" aria-hidden />}
        </span>
      </span>
      {gloss && (
        <span
          className="mt-0.5 block text-[11.5px]"
          style={{ color: "var(--color-text-tertiary)" }}
        >
          {gloss}
        </span>
      )}
    </button>
  );
}

function CheckRow({
  label,
  checked,
  onClick,
  swatch,
}: {
  label: string;
  checked: boolean;
  onClick: () => void;
  swatch?: React.CSSProperties;
}) {
  return (
    <button
      role="menuitemcheckbox"
      aria-checked={checked}
      onClick={onClick}
      className="flex w-full items-center gap-2 rounded px-1.5 py-1.5 text-left text-[12.5px] transition-colors hover:bg-[color:var(--color-slate-50)]"
      style={{ color: "var(--color-text-primary)" }}
    >
      <span
        className="grid h-3.5 w-3.5 place-items-center rounded-[3px] border"
        style={{
          borderColor: checked ? "var(--color-chrome)" : "var(--color-border)",
          backgroundColor: checked ? "var(--color-chrome)" : "transparent",
          color: "var(--color-text-on-brand)",
        }}
      >
        {checked && <Check className="h-2.5 w-2.5" aria-hidden />}
      </span>
      {swatch && (
        <span className="h-2.5 w-2.5 rounded-sm" style={swatch} aria-hidden />
      )}
      <span>{label}</span>
    </button>
  );
}

function FootGloss({ text }: { text: string }) {
  return (
    <div
      className="px-3 py-2 text-[11.5px]"
      style={{
        color: "var(--color-text-secondary)",
        borderTop: "1px solid var(--color-border)",
        backgroundColor: "var(--color-slate-50)",
      }}
    >
      {text}
    </div>
  );
}

/* ─────────────────── util ─────────────────── */

function useOutsideClose(open: boolean, close: () => void) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) close();
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [open, close]);
  return ref;
}
