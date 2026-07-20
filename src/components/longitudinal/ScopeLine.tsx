/**
 * Longitudinal — scope line.
 *
 * High-fidelity: both chips are click-open popovers again, and the Filter
 * button opens the full panel. Selections **do not re-scope** any data.
 * That is the honesty floor: the chip labels state what the numbers on the
 * page were actually computed against; re-labelling them while the data
 * stands still would put a false basis on a real number. So the menu
 * opens, options render, the active option shows checked, clicking one
 * moves the check and closes the menu — but the chip label, the Summary
 * tick, and the Days 100-line stay put.
 *
 * Filter applies as dismissible chips beside the two scope chips, each
 * with its own dismiss control. Charts and numbers remain unchanged.
 *
 * Option-key gaps discovered in the deck (see findings §Final pass):
 *   - Benchmark menu: no option keys authored — shows only the gloss.
 *   - Reference menu: none of six option keys authored — panel empty.
 *   - Filter: only Session-type group is authored.
 */
import { ChevronDown, Filter as FilterIcon, Check, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { copy } from "@/lib/copy-deck";
import { LegendPopover } from "./LegendPopover";
import type { LongiWindow } from "@/lib/longitudinal-data";

/* ─────────────────── filter state (demo-local) ─────────────────── */

type SessionTypeOpt = "matches" | "training";
type FilterState = { sessionType: SessionTypeOpt[] };
const EMPTY_FILTER: FilterState = { sessionType: [] };

export function ScopeLine({ window: w }: { window: LongiWindow }) {
  const [applied, setApplied] = useState<FilterState>(EMPTY_FILTER);

  const dismissSessionType = (opt: SessionTypeOpt) =>
    setApplied((s) => ({ ...s, sessionType: s.sessionType.filter((o) => o !== opt) }));

  return (
    <div className="flex min-w-0 flex-1 flex-wrap items-center gap-2">
      <BenchmarkChip />
      <Sep />
      <ReferenceChip />

      {applied.sessionType.map((opt) => (
        <AppliedChip
          key={`stype-${opt}`}
          label={
            opt === "matches"
              ? copy("longi.filter.opt.matches")
              : copy("longi.filter.opt.training")
          }
          onDismiss={() => dismissSessionType(opt)}
        />
      ))}

      <div className="ml-auto flex items-center gap-3">
        <FilterButton applied={applied} onApply={setApplied} />
        <LegendPopover window={w} />
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
      ·
    </span>
  );
}

function BenchmarkChip() {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState<string>("default");
  const wrapRef = useOutsideClose(open, () => setOpen(false));

  return (
    <div className="relative" ref={wrapRef}>
      <ChipButton open={open} onClick={() => setOpen((o) => !o)}>
        {copy("longi.scope.benchmarkChip")}
      </ChipButton>
      {open && (
        <Popover>
          <MenuRow
            checked={selected === "default"}
            label={copy("longi.scope.benchmarkChip")}
            onClick={() => {
              setSelected("default");
              setOpen(false);
            }}
          />
          <GapNote text={copy("longi.benchmark.gap")} />
          <FootGloss text={copy("longi.scope.benchmarkGloss")} />
        </Popover>
      )}
    </div>
  );
}

function ReferenceChip() {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState<string>("default");
  const wrapRef = useOutsideClose(open, () => setOpen(false));

  return (
    <div className="relative" ref={wrapRef}>
      <ChipButton open={open} onClick={() => setOpen((o) => !o)}>
        {copy("longi.scope.referenceChip")}
      </ChipButton>
      {open && (
        <Popover>
          <MenuRow
            checked={selected === "default"}
            label={copy("longi.scope.referenceChip")}
            onClick={() => {
              setSelected("default");
              setOpen(false);
            }}
          />
          <GapNote text={copy("longi.reference.gap")} />
        </Popover>
      )}
    </div>
  );
}

function ChipButton({
  children,
  open,
  onClick,
}: {
  children: React.ReactNode;
  open: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      aria-haspopup="menu"
      aria-expanded={open}
      className="inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-[12.5px] transition-colors hover:bg-[color:var(--color-slate-50)]"
      style={{
        borderColor: "var(--color-border)",
        color: "var(--color-text-secondary)",
        backgroundColor: "var(--color-surface-card)",
      }}
    >
      <span>{children}</span>
      <ChevronDown className="h-3 w-3 opacity-70" aria-hidden />
    </button>
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
  const [draft, setDraft] = useState<FilterState>(applied);
  const wrapRef = useOutsideClose(open, () => setOpen(false));

  const activeCount = applied.sessionType.length;

  const toggle = (opt: SessionTypeOpt) =>
    setDraft((s) => ({
      ...s,
      sessionType: s.sessionType.includes(opt)
        ? s.sessionType.filter((o) => o !== opt)
        : [...s.sessionType, opt],
    }));

  return (
    <div className="relative" ref={wrapRef}>
      <button
        onClick={() => {
          setDraft(applied);
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
          className="absolute right-0 top-full z-40 mt-2 w-[280px] overflow-hidden rounded-md border shadow-xl"
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

          <div className="px-3 py-2">
            <div
              className="type-microcaps mb-1.5"
              style={{ color: "var(--color-text-tertiary)" }}
            >
              {copy("longi.filter.group.sessionType")}
            </div>
            <div className="flex flex-col">
              <CheckRow
                label={copy("longi.filter.opt.matches")}
                checked={draft.sessionType.includes("matches")}
                onClick={() => toggle("matches")}
              />
              <CheckRow
                label={copy("longi.filter.opt.training")}
                checked={draft.sessionType.includes("training")}
                onClick={() => toggle("training")}
              />
            </div>
          </div>

          <div
            className="px-3 pb-2 text-[11.5px]"
            style={{ color: "var(--color-text-tertiary)" }}
          >
            {copy("longi.filter.gap")}
          </div>

          <div
            className="flex items-center justify-between gap-2 border-t px-3 py-2"
            style={{ borderColor: "var(--color-border)" }}
          >
            <button
              onClick={() => setDraft(EMPTY_FILTER)}
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
                  onApply(draft);
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

function MenuRow({
  label,
  checked,
  onClick,
}: {
  label: string;
  checked: boolean;
  onClick: () => void;
}) {
  return (
    <button
      role="menuitemradio"
      aria-checked={checked}
      onClick={onClick}
      className="flex w-full items-center justify-between gap-3 px-3 py-2 text-left text-[12.5px] transition-colors hover:bg-[color:var(--color-slate-100)]"
      style={{ color: "var(--color-text-primary)" }}
    >
      <span>{label}</span>
      {checked && <Check className="h-3.5 w-3.5" aria-hidden />}
    </button>
  );
}

function CheckRow({
  label,
  checked,
  onClick,
}: {
  label: string;
  checked: boolean;
  onClick: () => void;
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
      <span>{label}</span>
    </button>
  );
}

function GapNote({ text }: { text: string }) {
  return (
    <div
      className="px-3 py-2 text-[11.5px]"
      style={{
        color: "var(--color-text-tertiary)",
        borderTop: "1px dashed var(--color-border)",
      }}
    >
      {text}
    </div>
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
