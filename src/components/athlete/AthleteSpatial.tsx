/**
 * ST2 — Athlete page · Spatial section (Workstream 02 · prompt 4).
 *
 * Where they worked, this session. One pitch, their own density, from
 * `demo-spatial.ts`.
 *
 * Structure: an outer section (title + Heat/Trace toggle) wrapping ONE
 * `PitchField`. `PitchField` renders the pitch outline, either heat or
 * trace, the three-thirds numeric column, and the footer. It takes a
 * `SpatialField | null` and knows nothing about the section it lives in
 * — Workstream 03 will place a second `PitchField` beside the first at
 * identical costume for the subject-plus-peer pair.
 *
 * Costume rules folded in from the prompt:
 *   - Density ramp is a single blue: `--color-axis-work`, light to deep.
 *     No RAG. Density is magnitude; magnitude is never severity.
 *   - Field scales to THIS athlete's peak this session. Footer says so
 *     explicitly — the ramp's deep end is their maximum, never a shared
 *     scale. This wording is inherited by Workstream 03's pair build.
 *   - Thirds print as three labelled percentages, numbers only. NO
 *     bars — the numeric anchor is ratified; unratified bars in the
 *     source render drew each value at ~2× its true share against an
 *     unlabelled rail and contradicted the number printed next to it.
 *   - Unavailable state is designed at full size — faint pitch outline
 *     and one honest reason. No fabricated remedy: the system does not
 *     know the cause of missing positional data. The card states the
 *     absence and stops (2026-07-20 correction; the fix template that
 *     invented a mounting diagnosis is withdrawn).
 */


import { useState, type ReactElement } from "react";
import { copy, tmpl } from "@/lib/copy-deck";
import { demoAthletes, recordsForSession } from "@/lib/demo-library";
import { spatialFor, type SpatialField } from "@/lib/demo-spatial";

type Mode = "heat" | "trace";

type Props = {
  athleteId: string;
  sessionId: string;
  peerAthleteId?: string | null;
};

export function AthleteSpatial({ athleteId, sessionId, peerAthleteId = null }: Props) {
  const [mode, setMode] = useState<Mode>("heat");
  const field = spatialFor(athleteId, sessionId);
  const athlete = demoAthletes.find((a) => a.id === athleteId);
  const rec = recordsForSession(sessionId).find((r) => r.athleteId === athleteId);
  const minutes = rec?.minutes ?? 0;
  const athleteName = athlete?.name ?? "";

  const peerField = peerAthleteId ? spatialFor(peerAthleteId, sessionId) : null;
  const peer = peerAthleteId ? demoAthletes.find((a) => a.id === peerAthleteId) ?? null : null;
  const peerRec = peerAthleteId ? recordsForSession(sessionId).find((r) => r.athleteId === peerAthleteId) : null;
  const peerMinutes = peerRec?.minutes ?? 0;
  const peerName = peer?.name ?? "";
  const paired = Boolean(peerAthleteId);

  return (
    <section
      className="rounded-lg border"
      style={{
        backgroundColor: "var(--color-surface-card)",
        borderColor: "var(--color-border)",
      }}
      data-section="athlete-spatial"
    >
      <div
        className="flex items-center justify-between border-b px-5 py-2.5"
        style={{ borderColor: "var(--color-border)" }}
      >
        <h3 className="type-section-h" style={{ color: "var(--color-text-primary)" }}>
          {copy("athlete.spatial.title")}
        </h3>
        <ModeToggle value={mode} onChange={setMode} disabled={!field && !peerField} />
      </div>

      <div className="p-5">
        {paired ? (
          <div className="grid grid-cols-2 gap-5">
            <div>
              <div
                className="type-microcaps mb-2 text-[10.5px]"
                style={{ color: "var(--color-text-tertiary)" }}
              >
                {tmpl("athlete.peer.subjectHeadTemplate", { name: athleteName })}
              </div>
              <PitchField
                field={field}
                mode={mode}
                minutes={minutes}
                athleteName={athleteName}
              />
            </div>
            <div>
              <div
                className="type-microcaps mb-2 text-[10.5px]"
                style={{ color: "var(--color-text-tertiary)" }}
              >
                {tmpl("athlete.peer.peerHeadTemplate", { name: peerName })}
              </div>
              {peerField ? (
                <PitchField
                  field={peerField}
                  mode={mode}
                  minutes={peerMinutes}
                  athleteName={peerName}
                  showAttacking={false}
                />

              ) : (
                <PeerUnavailable athleteName={peerName} />
              )}
            </div>
          </div>
        ) : (
          <PitchField
            field={field}
            mode={mode}
            minutes={minutes}
            athleteName={athleteName}
          />
        )}
      </div>
    </section>
  );
}

function PeerUnavailable({ athleteName }: { athleteName: string }) {
  return (
    <div className="grid grid-cols-[1fr_180px] gap-6">
      <div>
        <svg
          viewBox={`0 0 ${VB_W} ${VB_H}`}
          className="block w-full"
          style={{ maxHeight: 380 }}
          aria-label={`no positional data recorded${athleteName ? ` for ${athleteName}` : ""}`}
        >
          <PitchOutline faint />
        </svg>
        <div
          className="mt-3 border-t pt-2 text-[12px]"
          style={{ borderColor: "var(--color-border)", color: "var(--color-text-secondary)" }}
        >
          <div>{copy("athlete.spatial.peer.unavailable")}</div>
        </div>
      </div>
      <div
        className="type-microcaps text-[10.5px]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        {copy("athlete.spatial.thirds.head")}
        <div className="mt-2 text-[12.5px]" style={{ color: "var(--color-text-tertiary)" }}>
          —
        </div>
      </div>
    </div>
  );
}

/* ─────────────────── Heat / Trace toggle ─────────────────── */

function ModeToggle({
  value,
  onChange,
  disabled,
}: {
  value: Mode;
  onChange: (m: Mode) => void;
  disabled?: boolean;
}) {
  return (
    <div
      className="inline-flex overflow-hidden rounded-md border text-[11.5px]"
      style={{ borderColor: "var(--color-border)" }}
      role="tablist"
      aria-label="Spatial mode"
    >
      {(["heat", "trace"] as const).map((m) => {
        const active = value === m;
        return (
          <button
            key={m}
            role="tab"
            aria-selected={active}
            disabled={disabled}
            onClick={() => onChange(m)}
            className="type-microcaps px-2.5 py-1 transition-colors disabled:opacity-50"
            style={{
              backgroundColor: active
                ? "var(--color-slate-100)"
                : "transparent",
              color: active
                ? "var(--color-text-primary)"
                : "var(--color-text-tertiary)",
              fontWeight: active ? 500 : 400,
            }}
          >
            {copy(m === "heat" ? "athlete.spatial.mode.heat" : "athlete.spatial.mode.trace")}
          </button>
        );
      })}
    </div>
  );
}

/* ─────────────────── one field ───────────────────
 * Public shape so Workstream 03 can drop a second field beside the first
 * at identical costume. Do not add a `muted` prop — muting one field in a
 * pair would be a false statement about that athlete.
 */

export function PitchField({
  field,
  mode,
  minutes,
  athleteName,
  showAttacking = true,
}: {
  field: SpatialField | null;
  mode: Mode;
  minutes: number;
  athleteName: string;
  showAttacking?: boolean;
}) {
  if (!field) {
    return <UnavailablePitch athleteName={athleteName} />;
  }
  return (
    <div className="grid grid-cols-[1fr_180px] gap-6">
      <div>
        <PitchSvg field={field} mode={mode} showAttacking={showAttacking} />

        <PitchFooter minutes={minutes} coveragePct={field.coveragePct} />
      </div>
      <ThirdsColumn thirds={field.thirds} />
    </div>
  );
}

/* ─────────────────── pitch SVG ─────────────────── */

// viewBox chosen so x = 0..100 is the attacking axis (defensive→attacking)
// and y = 0..65 is the width. Aspect ~ 1.54 : 1, close enough to a real
// pitch (~105 × 68m).
const VB_W = 100;
const VB_H = 65;

// Attacking direction = +x. Anchors in demo-spatial place x=0 at the
// team's own goal, x=100 at the attacking goal.

// Heat grid — 20 columns × 13 rows over the pitch. Points come in as
// x:0..100, y:0..100; we scale y into VB_H when drawing but bin on the
// raw 100×100 space so the coordinate contract with `demo-spatial` is
// unchanged.
const GRID_COLS = 20;
const GRID_ROWS = 13;

function PitchSvg({ field, mode }: { field: SpatialField; mode: Mode }) {
  return (
    <div className="relative">
      <svg
        viewBox={`0 0 ${VB_W} ${VB_H}`}
        className="block w-full"
        style={{ maxHeight: 380 }}
        aria-label={mode === "heat" ? "position density heat map" : "position trace"}
      >
        <PitchOutline />
        {mode === "heat" ? <HeatLayer field={field} /> : <TraceLayer field={field} />}
      </svg>
      <div
        className="type-microcaps absolute right-2 top-1 text-[9.5px]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        {copy("athlete.spatial.attacking")}
      </div>
    </div>
  );
}

function PitchOutline({ faint = false }: { faint?: boolean }) {
  const stroke = faint ? "var(--color-border)" : "var(--color-slate-300)";
  const sw = 0.25;
  return (
    <g fill="none" stroke={stroke} strokeWidth={sw} strokeLinejoin="round">
      {/* boundary */}
      <rect x={0.5} y={0.5} width={VB_W - 1} height={VB_H - 1} rx={0.6} />
      {/* centre line */}
      <line x1={VB_W / 2} y1={0.5} x2={VB_W / 2} y2={VB_H - 0.5} />
      {/* centre circle */}
      <circle cx={VB_W / 2} cy={VB_H / 2} r={6} />
      <circle cx={VB_W / 2} cy={VB_H / 2} r={0.4} fill={stroke} />
      {/* penalty boxes */}
      <rect x={0.5} y={(VB_H - 26) / 2} width={11} height={26} />
      <rect x={VB_W - 11.5} y={(VB_H - 26) / 2} width={11} height={26} />
      {/* six-yard boxes */}
      <rect x={0.5} y={(VB_H - 12) / 2} width={4} height={12} />
      <rect x={VB_W - 4.5} y={(VB_H - 12) / 2} width={4} height={12} />
      {/* goals */}
      <rect x={-0.6} y={(VB_H - 5.5) / 2} width={1.1} height={5.5} />
      <rect x={VB_W - 0.5} y={(VB_H - 5.5) / 2} width={1.1} height={5.5} />
    </g>
  );
}

function HeatLayer({ field }: { field: SpatialField }) {
  // Bin points into GRID_COLS × GRID_ROWS. Peak count = field's own max.
  // Ramp is `--color-axis-work` with variable opacity, light→deep.
  const cellW = 100 / GRID_COLS;
  const cellH = 100 / GRID_ROWS;
  const bins: number[][] = Array.from({ length: GRID_ROWS }, () =>
    new Array(GRID_COLS).fill(0),
  );
  for (const p of field.points) {
    const cx = Math.min(GRID_COLS - 1, Math.max(0, Math.floor(p.x / cellW)));
    const cy = Math.min(GRID_ROWS - 1, Math.max(0, Math.floor(p.y / cellH)));
    bins[cy][cx] += 1;
  }
  let peak = 0;
  for (const row of bins) for (const v of row) if (v > peak) peak = v;
  if (peak === 0) return null;

  const rects: ReactElement[] = [];
  const drawCellW = VB_W / GRID_COLS;
  const drawCellH = VB_H / GRID_ROWS;
  for (let r = 0; r < GRID_ROWS; r++) {
    for (let c = 0; c < GRID_COLS; c++) {
      const v = bins[r][c];
      if (v === 0) continue;
      // Non-linear ramp: sqrt spreads the lower tail so a lobe reads,
      // but the deep end is still reserved for the athlete's true peak.
      const t = Math.sqrt(v / peak);
      const opacity = 0.12 + t * 0.78; // 0.12 → 0.9
      rects.push(
        <rect
          key={`${r}-${c}`}
          x={c * drawCellW}
          y={r * drawCellH}
          width={drawCellW}
          height={drawCellH}
          fill="var(--color-axis-work)"
          opacity={opacity}
        />,
      );
    }
  }
  return <g>{rects}</g>;
}

function TraceLayer({ field }: { field: SpatialField }) {
  const scaleY = VB_H / 100;
  if (field.path.length === 0) return null;
  const d = field.path
    .map((p, i) => `${i === 0 ? "M" : "L"}${p.x.toFixed(2)},${(p.y * scaleY).toFixed(2)}`)
    .join(" ");
  const first = field.path[0];
  const last = field.path[field.path.length - 1];
  return (
    <g>
      <path
        d={d}
        fill="none"
        stroke="var(--color-axis-work)"
        strokeWidth={0.55}
        strokeLinejoin="round"
        strokeLinecap="round"
        opacity={0.85}
      />
      {/* kick-off — filled dot */}
      <g>
        <circle
          cx={first.x}
          cy={first.y * scaleY}
          r={1.1}
          fill="var(--color-axis-work)"
        />
        <text
          x={first.x + 1.5}
          y={first.y * scaleY + 0.4}
          fontSize={2.2}
          fill="var(--color-text-secondary)"
        >
          {copy("athlete.spatial.trace.kickoff")}
        </text>
      </g>
      {/* final whistle — outlined ring (not a coverage-hollow; it is a
          time-boundary marker on a trace layer, no ambiguity with the
          spine's hollow-coverage costume which lives on a horizontal
          track two sections up). */}
      <g>
        <circle
          cx={last.x}
          cy={last.y * scaleY}
          r={1.1}
          fill="none"
          stroke="var(--color-axis-work)"
          strokeWidth={0.4}
        />
        <text
          x={last.x - 1.5}
          y={last.y * scaleY + 0.4}
          fontSize={2.2}
          textAnchor="end"
          fill="var(--color-text-secondary)"
        >
          {copy("athlete.spatial.trace.finalWhistle")}
        </text>
      </g>
    </g>
  );
}

/* ─────────────────── thirds column (numbers only, no bars) ─────────────────── */

function ThirdsColumn({
  thirds,
}: {
  thirds: SpatialField["thirds"];
}) {
  const rows: { key: string; label: string; value: number }[] = [
    { key: "att", label: copy("athlete.spatial.thirds.attacking"), value: thirds.attackingPct },
    { key: "mid", label: copy("athlete.spatial.thirds.middle"), value: thirds.middlePct },
    { key: "def", label: copy("athlete.spatial.thirds.defensive"), value: thirds.defensivePct },
  ];
  return (
    <div className="flex flex-col gap-2">
      <div
        className="type-microcaps text-[10.5px]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        {copy("athlete.spatial.thirds.head")}
      </div>
      <div className="flex flex-col">
        {rows.map((r) => (
          <div
            key={r.key}
            className="flex items-baseline justify-between border-b py-1.5 last:border-b-0"
            style={{ borderColor: "var(--color-border)" }}
          >
            <span className="text-[12.5px]" style={{ color: "var(--color-text-primary)" }}>
              {r.label}
            </span>
            <span
              className="type-num text-[13px] font-semibold"
              style={{ color: "var(--color-text-primary)" }}
            >
              {r.value}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─────────────────── footer — sampling + scaling basis ─────────────────── */

function PitchFooter({ minutes, coveragePct }: { minutes: number; coveragePct: number }) {
  return (
    <div
      className="mt-3 border-t pt-2 text-[11.5px]"
      style={{ borderColor: "var(--color-border)", color: "var(--color-text-tertiary)" }}
    >
      <div className="type-num">
        {tmpl("athlete.spatial.footer.sampledTemplate", {
          minutes,
          cov: coveragePct,
        })}
      </div>
      <div className="mt-0.5">{copy("athlete.spatial.footer.scale")}</div>
    </div>
  );
}

/* ─────────────────── unavailable state — full-size ─────────────────── */

function UnavailablePitch({ athleteName }: { athleteName: string }) {
  return (
    <div className="grid grid-cols-[1fr_180px] gap-6">
      <div>
        <svg
          viewBox={`0 0 ${VB_W} ${VB_H}`}
          className="block w-full"
          style={{ maxHeight: 380 }}
          aria-label={`no positional data recorded${athleteName ? ` for ${athleteName}` : ""}`}
        >
          <PitchOutline faint />
        </svg>
        <div
          className="mt-3 border-t pt-2 text-[12px]"
          style={{ borderColor: "var(--color-border)", color: "var(--color-text-secondary)" }}
        >
          <div>{copy("athlete.spatial.unavailable.reason")}</div>
          {/* No remedial sentence: the system does not know the cause, and
              this card must not be the one place in the product that guesses.
              Withdrawal recorded in findings 2026-07-20. */}
        </div>
      </div>
      <div
        className="type-microcaps text-[10.5px]"
        style={{ color: "var(--color-text-tertiary)" }}
      >
        {copy("athlete.spatial.thirds.head")}
        <div className="mt-2 text-[12.5px]" style={{ color: "var(--color-text-tertiary)" }}>
          —
        </div>
      </div>
    </div>
  );
}
