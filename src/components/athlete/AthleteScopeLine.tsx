/**
 * Athlete page scope line.
 *
 * One sentence, fixed order:
 *   [Reference chip] · periods [all N]  … [flag chip?] · [peer chip?]
 *
 * The Reference menu reuses `longi.ref.*` keys (shared object — namespace
 * rename deferred to record-close, not a duplication to fix now).
 * A non-default Reference selection tints the chip slate.
 *
 * `same_opponent` hides on training sessions.
 * Flag chip renders only when this athlete is in TIER1_ROWS_DEFAULT and
 * the pinned session is current.
 */
import { ChevronDown, Check, Flag, X } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { copy, tmpl } from "@/lib/copy-deck";
import { demoSessions, demoAthletes } from "@/lib/demo-library";
import { TIER1_ROWS_DEFAULT } from "@/lib/session-flags";
import { periodOptionsFor, type PeriodOption } from "@/lib/athlete-data";
import { REFERENCE_OPTIONS, type ReferenceKind } from "@/lib/session-scope";

const PINNED_SESSION_ID = "s-2026-07-04-dortmund";

// Athlete uses Session's Reference set verbatim; the own_typical label is
// dynamic and echoes Session's helper — "their typical match" on a match,
// "their typical {dayCode}" on other days.
export type RefKind = ReferenceKind;

const REF_GROUPS: Array<{ kind: RefKind }[]> = [
  [{ kind: "own_typical" }, { kind: "last_n" }, { kind: "season" }],
  [{ kind: "positional" }, { kind: "cohort" }],
  [{ kind: "same_opponent" }],
];

const DEFAULT_REF: RefKind = "own_typical";

function ownTypicalLabel(
  session: { type: string; dayCode: string } | undefined | null,
): string {
  if (!session) return "their typical match";
  return session.type === "match"
    ? "their typical match"
    : `their typical ${session.dayCode}`;
}

function refLabelFor(
  kind: RefKind,
  session: { type: string; dayCode: string } | undefined | null,
): string {
  if (kind === "own_typical") return ownTypicalLabel(session);
  const opt = REFERENCE_OPTIONS.find((o) => o.kind === kind);
  return opt ? opt.label : String(kind);
}

type Props = {
  athleteId: string;
  sessionId: string;
  onSessionChange: (id: string) => void;
  peerId?: string | null;
  onPeerChange?: (id: string | null) => void;
};

export function AthleteScopeLine({ athleteId, sessionId, onSessionChange, peerId, onPeerChange }: Props) {
  const [refKind, setRefKind] = useState<RefKind>(DEFAULT_REF);
  const [flagDismissed, setFlagDismissed] = useState(false);

  const activeSession =
    demoSessions.find((s) => s.id === sessionId) ?? demoSessions.find((s) => s.id === PINNED_SESSION_ID);

  const isMatch = activeSession?.type === "match";
  const isPinned = activeSession?.id === PINNED_SESSION_ID;

  const periodOpts = useMemo(
    () => (activeSession ? periodOptionsFor(activeSession.id) : []),
    [activeSession],
  );

  const [periodSel, setPeriodSel] = useState<string>("all");

  const tier1Row = TIER1_ROWS_DEFAULT.find((r) => r.id === athleteId);
  const showFlag = Boolean(tier1Row) && isPinned && !flagDismissed;

  return (
    <div className="flex min-w-0 flex-1 items-center gap-2 text-[12.5px]">
      <ReferenceChip
        value={refKind}
        onChange={setRefKind}
        session={activeSession}
        showSameOpponent={isMatch}
      />
      <Sep />
      <span style={{ color: "var(--color-text-tertiary)" }}>
        {copy("athlete.scope.periodsLabel")}
      </span>
      <PeriodsChip
        value={periodSel}
        onChange={setPeriodSel}
        options={periodOpts}
      />
      {onPeerChange && (
        <>
          <Sep />
          <span style={{ color: "var(--color-text-tertiary)" }}>
            {copy("athlete.scope.peerLabel")}
          </span>
          <PeerChip
            subjectId={athleteId}
            value={peerId ?? null}
            onChange={onPeerChange}
          />
        </>
      )}

      {showFlag && tier1Row && (
        <>
          <span className="mx-1" style={{ color: "var(--color-text-tertiary)" }}>
            {" "}
          </span>
          <FlagChip
            metric={tier1Row.reason}
            onDismiss={() => setFlagDismissed(true)}
          />
        </>
      )}
    </div>
  );
}

/* ─────────────────── peer chip ─────────────────── */

function PeerChip({
  subjectId,
  value,
  onChange,
}: {
  subjectId: string;
  value: string | null;
  onChange: (id: string | null) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useDocClick(ref, open, () => setOpen(false));
  const roster = demoAthletes as unknown as ReadonlyArray<{ id: string; name: string; posDetail?: string }>;
  const eligible = roster.filter((a) => a.id !== subjectId);
  const active = value ? roster.find((a) => a.id === value) : null;
  const label = active ? active.name : copy("athlete.scope.peerNone");
  const changed = value != null;

  return (
    <div className="relative" ref={ref}>
      <ChipButton onClick={() => setOpen((o) => !o)} changed={changed}>
        <span className="truncate max-w-[160px]">{label}</span>
        <ChevronDown className="ml-1 h-3.5 w-3.5 opacity-70" aria-hidden />
      </ChipButton>
      {open && (
        <PopoverShell>
          <div
            className="border-b px-3 py-2 text-[11.5px]"
            style={{
              borderColor: "var(--color-border)",
              color: "var(--color-text-tertiary)",
            }}
          >
            {copy("athlete.scope.peerHead")}
          </div>
          <button
            onClick={() => {
              onChange(null);
              setOpen(false);
            }}
            className="flex w-full items-center gap-2 px-3 py-1.5 text-left text-[12.5px] transition-colors hover:bg-[color:var(--color-slate-100)]"
          >
            {value == null ? (
              <Check className="h-3.5 w-3.5" aria-hidden />
            ) : (
              <span className="inline-block h-3.5 w-3.5" aria-hidden />
            )}
            <span>{copy("athlete.scope.peerNone")}</span>
          </button>
          <div aria-hidden className="h-px" style={{ backgroundColor: "var(--color-border)" }} />
          {eligible.map((a) => {
            const isActive = a.id === value;
            return (
              <button
                key={a.id}
                onClick={() => {
                  onChange(a.id);
                  setOpen(false);
                }}
                className="flex w-full items-center justify-between gap-3 px-3 py-1.5 text-left text-[12.5px] transition-colors hover:bg-[color:var(--color-slate-100)]"
              >
                <span className="flex items-center gap-2">
                  {isActive ? (
                    <Check className="h-3.5 w-3.5" aria-hidden />
                  ) : (
                    <span className="inline-block h-3.5 w-3.5" aria-hidden />
                  )}
                  <span>{a.name}</span>
                </span>
                {a.posDetail && (
                  <span
                    className="type-microcaps"
                    style={{ color: "var(--color-text-tertiary)" }}
                  >
                    {a.posDetail}
                  </span>
                )}
              </button>
            );
          })}
        </PopoverShell>
      )}
    </div>
  );
}

/* ─────────────────── reference chip ─────────────────── */

function ReferenceChip({
  value,
  onChange,
  session,
  showSameOpponent,
}: {
  value: RefKind;
  onChange: (k: RefKind) => void;
  session: { type: string; dayCode: string } | undefined | null;
  showSameOpponent: boolean;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useDocClick(ref, open, () => setOpen(false));

  const changed = value !== DEFAULT_REF;
  const label = refLabelFor(value, session);

  return (
    <div className="relative" ref={ref}>
      <ChipButton onClick={() => setOpen((o) => !o)} changed={changed}>
        <span className="truncate max-w-[180px]">{label}</span>
        <ChevronDown className="ml-1 h-3.5 w-3.5 opacity-70" aria-hidden />
      </ChipButton>
      {open && (
        <PopoverShell>
          <div
            className="border-b px-3 py-2 text-[11.5px]"
            style={{
              borderColor: "var(--color-border)",
              color: "var(--color-text-tertiary)",
            }}
          >
            {copy("menu.titleReference")}
          </div>
          {REF_GROUPS.map((group, gi) => {
            const items = group.filter(
              (o) => showSameOpponent || o.kind !== "same_opponent",
            );
            if (items.length === 0) return null;
            return (
              <div key={gi}>
                {gi > 0 && (
                  <div
                    aria-hidden
                    className="h-px"
                    style={{ backgroundColor: "var(--color-border)" }}
                  />
                )}
                {items.map((o) => {
                  const active = o.kind === value;
                  const isDefault = o.kind === DEFAULT_REF;
                  return (
                    <button
                      key={o.kind}
                      onClick={() => {
                        onChange(o.kind);
                        setOpen(false);
                      }}
                      className="flex w-full items-start justify-between gap-3 px-3 py-1.5 text-left text-[12.5px] transition-colors hover:bg-[color:var(--color-slate-100)]"
                    >
                      <span className="flex items-start gap-2">
                        {active ? (
                          <Check className="mt-0.5 h-3.5 w-3.5" aria-hidden />
                        ) : (
                          <span className="mt-0.5 inline-block h-3.5 w-3.5" aria-hidden />
                        )}
                        <span>
                          <span className="block">{refLabelFor(o.kind, session)}</span>
                          <span
                            className="block text-[11.5px]"
                            style={{ color: "var(--color-text-tertiary)" }}
                          >
                            {copy(`readingLine.gloss.${o.kind}`)}
                          </span>
                        </span>
                      </span>
                      {isDefault && (
                        <span
                          className="type-microcaps whitespace-nowrap"
                          style={{ color: "var(--color-text-tertiary)" }}
                        >
                          default
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            );
          })}
        </PopoverShell>
      )}
    </div>
  );
}

/* ─────────────────── periods chip ─────────────────── */

function PeriodsChip({
  value,
  onChange,
  options,
}: {
  value: string;
  onChange: (v: string) => void;
  options: PeriodOption[];
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useDocClick(ref, open, () => setOpen(false));

  const active = options.find((o) => o.id === value) ?? options[0];
  const changed = value !== "all";
  if (!active) return null;

  return (
    <div className="relative" ref={ref}>
      <ChipButton onClick={() => setOpen((o) => !o)} changed={changed}>
        <span>{active.label}</span>
        <ChevronDown className="ml-1 h-3.5 w-3.5 opacity-70" aria-hidden />
      </ChipButton>
      {open && (
        <PopoverShell>
          {options.map((o) => {
            const isActive = o.id === value;
            return (
              <button
                key={o.id}
                onClick={() => {
                  onChange(o.id);
                  setOpen(false);
                }}
                className="flex w-full items-center gap-2 px-3 py-1.5 text-left text-[12.5px] transition-colors hover:bg-[color:var(--color-slate-100)]"
              >
                {isActive ? (
                  <Check className="h-3.5 w-3.5" aria-hidden />
                ) : (
                  <span className="inline-block h-3.5 w-3.5" aria-hidden />
                )}
                <span>{o.label}</span>
              </button>
            );
          })}
        </PopoverShell>
      )}
    </div>
  );
}

/* ─────────────────── flag chip ─────────────────── */

function FlagChip({
  metric,
  onDismiss,
}: {
  metric: string;
  onDismiss: () => void;
}) {
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-[12px]"
      style={{
        borderColor: "var(--color-border)",
        backgroundColor: "var(--color-slate-100)",
        color: "var(--color-text-secondary)",
      }}
    >
      <Flag className="h-3 w-3" aria-hidden />
      <span>{tmpl("athlete.scope.flagTemplate", { metric })}</span>
      <button
        onClick={onDismiss}
        aria-label={copy("athlete.scope.flagDismissAria")}
        className="grid h-4 w-4 place-items-center rounded transition-colors hover:bg-[color:var(--color-border)]"
      >
        <X className="h-3 w-3" aria-hidden />
      </button>
    </span>
  );
}

/* ─────────────────── shared bits ─────────────────── */

function ChipButton({
  children,
  onClick,
  changed,
}: {
  children: React.ReactNode;
  onClick: () => void;
  changed: boolean;
}) {
  return (
    <button
      onClick={onClick}
      className={`inline-flex items-center rounded-md border px-2 py-0.5 text-[12.5px] transition-colors hover:bg-[color:var(--color-slate-100)] ${changed ? "chip-changed" : ""}`}
      style={{
        borderColor: "var(--color-border)",
        color: "var(--color-text-primary)",
        backgroundColor: "var(--color-surface-card)",
      }}
    >
      {children}
    </button>
  );
}

function PopoverShell({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="absolute left-0 top-8 z-40 max-h-[420px] w-72 overflow-auto rounded-md border shadow-lg"
      style={{
        backgroundColor: "var(--color-surface-card)",
        borderColor: "var(--color-border)",
        color: "var(--color-text-primary)",
      }}
      role="menu"
    >
      {children}
    </div>
  );
}

function Sep() {
  return (
    <span style={{ color: "var(--color-text-tertiary)" }}>·</span>
  );
}

function useDocClick(
  ref: React.RefObject<HTMLDivElement | null>,
  open: boolean,
  close: () => void,
) {
  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) close();
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [open, close, ref]);
}
