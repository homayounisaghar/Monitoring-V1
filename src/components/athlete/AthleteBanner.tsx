/**
 * Athlete page banner — dark navy, one row, subject-owning.
 *
 * The name + chevron is the page's identity control: clicking it opens a
 * roster popover; selection re-scopes the page to a different athlete.
 * Position detail, participation + minutes, and max velocity print inline.
 *
 * Bio (age/height/weight) fields do not exist in the current data model,
 * so the bio chevron is intentionally omitted. Recorded in findings.
 * Jersey number is likewise absent from the data — omitted.
 */
import { ChevronDown } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { AthleteAvatar } from "@/components/data/AthleteAvatar";
import { demoAthletes, recordsForSession } from "@/lib/demo-library";
import { copy, tmpl } from "@/lib/copy-deck";

type Props = {
  athleteId: string;
  sessionId: string;
  onAthleteChange: (id: string) => void;
};

export function AthleteBanner({ athleteId, onAthleteChange }: Props) {
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, [open]);

  const athlete = demoAthletes.find((a) => a.id === athleteId) ?? demoAthletes[0];
  const s = currentSession;
  const sessionRow = squad.find((a) => a.id === athlete.id);
  const participation = sessionRow?.participation;
  const minutes = sessionRow?.minutes ?? 0;

  return (
    <div
      className="rounded-lg"
      style={{
        backgroundColor: "var(--color-chrome)",
        color: "var(--color-text-on-brand)",
      }}
    >
      <div className="flex h-[52px] items-center justify-between gap-6 px-5">
        <div className="flex min-w-0 items-center gap-x-2.5">
          <AthleteAvatar id={athlete.id} name={athlete.name} size={28} />

          <div className="relative" ref={menuRef}>
            <button
              onClick={() => setOpen((o) => !o)}
              aria-haspopup="menu"
              aria-expanded={open}
              className="flex items-center gap-1 rounded px-1 py-0.5 transition-colors"
              onMouseEnter={(e) =>
                (e.currentTarget.style.backgroundColor =
                  "color-mix(in oklab, white 8%, transparent)")
              }
              onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
            >
              <span className="truncate text-[15px] font-semibold tracking-tight">
                {athlete.name}
              </span>
              <ChevronDown className="h-3.5 w-3.5 opacity-80" aria-hidden />
            </button>

            {open && (
              <div
                role="menu"
                className="absolute left-0 top-9 z-40 max-h-[420px] w-72 overflow-auto rounded-md border shadow-lg"
                style={{
                  backgroundColor: "var(--color-surface-card)",
                  borderColor: "var(--color-border)",
                  color: "var(--color-text-primary)",
                }}
              >
                <div
                  className="type-microcaps border-b px-3 py-2"
                  style={{
                    borderColor: "var(--color-border)",
                    color: "var(--color-text-tertiary)",
                  }}
                >
                  {copy("athlete.banner.rosterHead")}
                </div>
                {demoAthletes.map((a) => {
                  const active = a.id === athlete.id;
                  return (
                    <button
                      key={a.id}
                      role="menuitemradio"
                      aria-checked={active}
                      onClick={() => {
                        onAthleteChange(a.id);
                        setOpen(false);
                      }}
                      className="flex w-full items-center justify-between gap-3 px-3 py-1.5 text-left text-[12.5px] transition-colors hover:bg-[color:var(--color-slate-100)]"
                    >
                      <span className="flex items-center gap-2">
                        <AthleteAvatar id={a.id} name={a.name} size={20} />
                        <span>{a.name}</span>
                      </span>
                      <span
                        className="type-num"
                        style={{
                          color: active
                            ? "var(--color-text-primary)"
                            : "var(--color-text-tertiary)",
                          fontWeight: active ? 600 : 400,
                        }}
                      >
                        {a.posDetail}
                      </span>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          <span
            className="type-microcaps rounded px-1.5 py-0.5"
            style={{
              backgroundColor: "color-mix(in oklab, white 12%, transparent)",
              color: "var(--color-slate-300)",
            }}
          >
            {athlete.posDetail}
          </span>

          <span
            className="whitespace-nowrap text-[12.5px]"
            style={{ color: "var(--color-slate-300)" }}
          >
            {participation ? (
              <>
                <span>{participation.toLowerCase()}</span>
                {minutes > 0 && (
                  <>
                    <Sep />
                    <span className="type-num">{minutes}&apos;</span>
                  </>
                )}
              </>
            ) : (
              <span>did not participate</span>
            )}
            <Sep />
            <span className="type-num">
              {tmpl("athlete.banner.maxVelTemplate", { v: athlete.maxVelKmh.toFixed(1) })}
            </span>
            <Sep />
            <span>{weekdayDayMonthYear(s.dateISO)}</span>
          </span>
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
