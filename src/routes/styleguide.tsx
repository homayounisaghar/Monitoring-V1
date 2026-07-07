import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/styleguide")({
  head: () => ({
    meta: [
      { title: "ST2 — Styleguide" },
      { name: "description", content: "ST2 design system: tokens, type, and core data objects." },
      { name: "robots", content: "noindex" },
    ],
  }),
  component: Styleguide,
});

/* ------------------------------------------------------------------ */
/* Core data objects                                                   */
/* ------------------------------------------------------------------ */

type Axis = "work" | "cost" | "neutral";

function axisColor(axis: Axis) {
  if (axis === "work") return "var(--color-axis-work)";
  if (axis === "cost") return "var(--color-axis-cost)";
  return "var(--color-data-ink)";
}

/**
 * ValueOnTrack — canonical comparison object.
 * Two scale modes: "deviation" (window centred on reference, default ±40%)
 * and "shared" (absolute scale; reference tick placed on shared scale).
 */
function ValueOnTrack({
  mode,
  axis = "neutral",
  value,
  reference,
  referenceBandPct,
  windowPct = 0.4,
  scaleMin,
  scaleMax,
  unit,
  deltaAbs,
  baselineState = "mature",
}: {
  mode: "deviation" | "shared";
  axis?: Axis;
  value: number;
  reference: number;
  /** Half-width of the reference's normal variation, as a fraction of reference (deviation mode)
   *  or in absolute scale units (shared mode). */
  referenceBandPct?: number;
  windowPct?: number;
  scaleMin?: number;
  scaleMax?: number;
  unit?: string;
  deltaAbs?: string;
  /** "mature" = narrow band, "young" = wide band, "building" = withhold reference entirely. */
  baselineState?: "mature" | "young" | "building";
}) {
  const color = axisColor(axis);
  const withheld = baselineState === "building";
  const deltaPct = ((value - reference) / reference) * 100;
  const deltaLabel = `${deltaPct >= 0 ? "+" : ""}${deltaPct.toFixed(0)}%`;

  let posPct: number;
  let refPct: number;
  let bandLeftPct = 0;
  let bandRightPct = 0;
  let clamped = false;

  if (mode === "deviation") {
    const raw = (value - reference) / reference;
    if (raw > windowPct) {
      posPct = 100;
      clamped = true;
    } else if (raw < -windowPct) {
      posPct = 0;
      clamped = true;
    } else {
      posPct = ((raw + windowPct) / (windowPct * 2)) * 100;
    }
    refPct = 50;
    const halfBandFrac = referenceBandPct ?? 0.08;
    bandLeftPct = Math.max(0, ((-halfBandFrac + windowPct) / (windowPct * 2)) * 100);
    bandRightPct = Math.min(100, ((halfBandFrac + windowPct) / (windowPct * 2)) * 100);
  } else {
    const min = scaleMin ?? 0;
    const max = scaleMax ?? 1;
    posPct = Math.max(0, Math.min(100, ((value - min) / (max - min)) * 100));
    refPct = Math.max(0, Math.min(100, ((reference - min) / (max - min)) * 100));
    const halfBandAbs = referenceBandPct ?? (max - min) * 0.05;
    bandLeftPct = Math.max(0, ((reference - halfBandAbs - min) / (max - min)) * 100);
    bandRightPct = Math.min(100, ((reference + halfBandAbs - min) / (max - min)) * 100);
  }

  return (
    <div className="flex items-center gap-3">
      <div className="relative h-7 flex-1">
        {/* Track band */}
        <div
          className="absolute left-0 right-0 top-1/2 h-[7px] -translate-y-1/2 rounded-full"
          style={{ backgroundColor: "var(--color-data-band)" }}
        />
        {/* Reference band — normal variation window (withheld when baseline is still building) */}
        {!withheld && (
          <div
            className="absolute top-1/2 h-[11px] -translate-y-1/2 rounded-sm"
            style={{
              left: `${bandLeftPct}%`,
              width: `${bandRightPct - bandLeftPct}%`,
              backgroundColor: "var(--color-reference-band)",
            }}
            aria-label="reference band — typical variation"
          />
        )}
        {/* Reference tick */}
        {!withheld && (
          <div
            className="absolute top-1/2 h-4 w-[2px] -translate-x-1/2 -translate-y-1/2 rounded-sm"
            style={{ left: `${refPct}%`, backgroundColor: "var(--color-data-reference)" }}
            aria-label="reference"
          />
        )}
        {/* Value dot */}
        <div
          className="absolute top-1/2 h-3.5 w-3.5 -translate-x-1/2 -translate-y-1/2 rounded-full ring-2 ring-white"
          style={{ left: `${posPct}%`, backgroundColor: color }}
          aria-label="value"
        />
        {/* Overflow marker */}
        {clamped && !withheld && (
          <div
            className="absolute top-1/2 -translate-y-1/2 type-num text-[10px] font-semibold"
            style={{
              [deltaPct > 0 ? "right" : "left"]: "-4px",
              color: "var(--color-text-secondary)",
            }}
          >
            {deltaPct > 0 ? "▸" : "◂"}
          </div>
        )}
      </div>
      <div className="flex min-w-[130px] items-baseline justify-end gap-2">
        <span className="type-num text-sm font-semibold" style={{ color: "var(--color-text-primary)" }}>
          {value.toLocaleString()}
          {unit ? <span className="type-data-label ml-0.5">{unit}</span> : null}
        </span>
        {withheld ? (
          <span className="type-data-label italic" title="Baseline still building — no reference yet">
            baseline building
          </span>
        ) : (
          <span
            className="type-num text-xs font-medium"
            style={{ color: "var(--color-text-secondary)" }}
            title={deltaAbs ? `Δ ${deltaAbs}` : undefined}
          >
            {deltaLabel}
          </span>
        )}
      </div>
    </div>
  );
}

/**
 * GapPair — external vs internal on a shared % scale.
 * External = filled blue circle. Internal = open purple ring.
 * Slate connector = the gap. Printed delta in signed pts.
 */
function GapPair({
  externalPct,
  internalPct,
}: {
  externalPct: number;
  internalPct: number;
}) {
  const left = Math.min(externalPct, internalPct);
  const right = Math.max(externalPct, internalPct);
  const gapPts = externalPct - internalPct;
  const gapLabel = `${gapPts >= 0 ? "+" : ""}${gapPts.toFixed(0)} pts`;

  return (
    <div className="space-y-2">
      <div className="relative h-8">
        <div
          className="absolute left-0 right-0 top-1/2 h-[7px] -translate-y-1/2 rounded-full"
          style={{ backgroundColor: "var(--color-data-band)" }}
        />
        {/* Connector */}
        <div
          className="absolute top-1/2 h-[2px] -translate-y-1/2"
          style={{
            left: `${left}%`,
            width: `${right - left}%`,
            backgroundColor: "var(--color-slate-400)",
          }}
        />
        {/* External — filled circle */}
        <div
          className="absolute top-1/2 h-3.5 w-3.5 -translate-x-1/2 -translate-y-1/2 rounded-full ring-2 ring-white"
          style={{ left: `${externalPct}%`, backgroundColor: "var(--color-axis-work)" }}
          aria-label="external — work"
        />
        {/* Internal — open ring */}
        <div
          className="absolute top-1/2 h-3.5 w-3.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white"
          style={{
            left: `${internalPct}%`,
            border: "2px solid var(--color-axis-cost)",
          }}
          aria-label="internal — cost"
        />
      </div>
      <div className="flex items-center justify-between type-data-label">
        <div className="flex items-center gap-4">
          <span className="inline-flex items-center gap-1.5">
            <span
              className="h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: "var(--color-axis-work)" }}
            />
            External — work
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span
              className="h-2.5 w-2.5 rounded-full bg-white"
              style={{ border: "2px solid var(--color-axis-cost)" }}
            />
            Internal — cost
          </span>
        </div>
        <span className="type-num font-semibold" style={{ color: "var(--color-text-primary)" }}>
          {gapLabel}
        </span>
      </div>
    </div>
  );
}

/**
 * TrustMark — one costume at every size.
 * Leading dot + hatched veil on the qualified mark + coverage printed on value.
 */
function TrustMark({
  size = "md",
  value,
  unit,
  coverage,
}: {
  size?: "sm" | "md" | "lg";
  value: string;
  unit?: string;
  coverage: number; // 0-100
}) {
  const dot = { sm: "h-1.5 w-1.5", md: "h-2 w-2", lg: "h-2.5 w-2.5" }[size];
  const veilH = { sm: "h-3", md: "h-4", lg: "h-5" }[size];
  const veilW = { sm: "w-10", md: "w-14", lg: "w-20" }[size];
  const num = { sm: "text-xs", md: "text-sm", lg: "text-base" }[size];

  return (
    <div className="inline-flex items-center gap-2">
      <span
        className={`${dot} shrink-0 rounded-full`}
        style={{ backgroundColor: "var(--color-trust-dot)" }}
        aria-hidden
      />
      <div className="relative inline-flex items-baseline gap-1">
        <span
          className={`veil-hatch absolute inset-x-0 top-1/2 -translate-y-1/2 ${veilH} ${veilW} rounded-sm opacity-70`}
          aria-hidden
        />
        <span
          className={`type-num ${num} relative font-semibold`}
          style={{ color: "var(--color-text-primary)" }}
        >
          {value}
          {unit ? <span className="type-data-label ml-0.5">{unit}</span> : null}
        </span>
      </div>
      <span className="type-data-label type-num">— {coverage}% cov</span>
    </div>
  );
}

/**
 * SeverityGlyph — Attention card only. Always glyph + word.
 */
function SeverityGlyph({ tier }: { tier: "escalate" | "notice" }) {
  if (tier === "escalate") {
    return (
      <span
        className="inline-flex items-center gap-1.5 rounded px-1.5 py-0.5 type-micro"
        style={{
          backgroundColor: "var(--color-escalate-surface)",
          color: "var(--color-escalate-ink)",
        }}
      >
        <svg width="10" height="10" viewBox="0 0 10 10" aria-hidden>
          <polygon points="5,1 9.5,9 0.5,9" fill="currentColor" />
        </svg>
        escalate
      </span>
    );
  }
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded px-1.5 py-0.5 type-micro"
      style={{
        backgroundColor: "var(--color-notice-surface)",
        color: "var(--color-notice-ink)",
      }}
    >
      <svg width="10" height="10" viewBox="0 0 10 10" aria-hidden>
        <polygon points="5,1 9,5 5,9 1,5" fill="currentColor" />
      </svg>
      notice
    </span>
  );
}

/* ------------------------------------------------------------------ */
/* Styleguide-only presentational helpers                              */
/* ------------------------------------------------------------------ */

function Section({
  title,
  desc,
  children,
}: {
  title: string;
  desc: string;
  children: React.ReactNode;
}) {
  return (
    <section className="space-y-4">
      <header className="space-y-1">
        <h2 className="type-section-h">{title}</h2>
        <p className="type-section-desc">{desc}</p>
      </header>
      {children}
    </section>
  );
}

function Card({
  eyebrow,
  children,
}: {
  eyebrow?: string;
  children: React.ReactNode;
}) {
  return (
    <div
      className="rounded-lg p-5"
      style={{
        backgroundColor: "var(--color-surface-card)",
        border: "1px solid var(--color-border)",
      }}
    >
      {eyebrow ? <div className="type-card-eyebrow mb-3">{eyebrow}</div> : null}
      {children}
    </div>
  );
}

function Swatch({
  token,
  hex,
  name,
  dark,
}: {
  token: string;
  hex: string;
  name: string;
  dark?: boolean;
}) {
  return (
    <div className="space-y-1.5">
      <div
        className="h-14 rounded-md"
        style={{ backgroundColor: hex, border: "1px solid var(--color-border)" }}
      />
      <div className="space-y-0.5">
        <div
          className="type-micro"
          style={{ color: dark ? "var(--color-text-primary)" : "var(--color-text-secondary)" }}
        >
          {name}
        </div>
        <div className="type-num text-[11px]" style={{ color: "var(--color-text-tertiary)" }}>
          {token}
        </div>
        <div className="type-num text-[11px]" style={{ color: "var(--color-text-tertiary)" }}>
          {hex}
        </div>
      </div>
    </div>
  );
}

function ZoneRamp({
  axis,
  label,
}: {
  axis: "work" | "cost";
  label: string;
}) {
  return (
    <div className="space-y-2">
      <div className="type-col-head">{label}</div>
      <div className="flex overflow-hidden rounded-md" style={{ border: "1px solid var(--color-border)" }}>
        {[1, 2, 3, 4, 5].map((n) => (
          <div
            key={n}
            className="flex h-14 flex-1 items-end justify-center pb-1.5 type-num text-[10.5px]"
            style={{
              backgroundColor: `var(--color-zone-${axis}-${n})`,
              color: n >= 4 ? "white" : "var(--color-slate-800)",
            }}
          >
            Z{n}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Page                                                                */
/* ------------------------------------------------------------------ */

function Styleguide() {
  return (
    <div className="min-h-screen" style={{ backgroundColor: "var(--color-canvas)" }}>
      {/* Chrome banner — persistent nav look */}
      <header
        className="flex h-14 items-center px-6"
        style={{ backgroundColor: "var(--color-chrome)", color: "white" }}
      >
        <div className="type-micro" style={{ letterSpacing: "0.12em" }}>
          ST2 · Styleguide
        </div>
      </header>

      <main className="mx-auto max-w-[1440px] space-y-12 px-8 py-10">
        {/* Palette */}
        <Section
          title="Palette"
          desc="Slate is the neutral spine. Brand green is identity and primary action only — never quality."
        >
          <Card eyebrow="Slate spine">
            <div className="grid grid-cols-10 gap-3">
              {[
                ["50", "#F8FAFC"],
                ["100", "#F1F5F9"],
                ["200", "#E2E8F0"],
                ["300", "#CBD5E1"],
                ["400", "#94A3B8"],
                ["500", "#64748B"],
                ["600", "#475569"],
                ["700", "#334155"],
                ["800", "#1E293B"],
                ["900", "#0F172A"],
              ].map(([n, hex]) => (
                <Swatch key={n} name={`slate-${n}`} token={`--slate-${n}`} hex={hex} />
              ))}
            </div>
          </Card>

          <div className="grid grid-cols-3 gap-4">
            <Card eyebrow="Brand & chrome">
              <div className="grid grid-cols-3 gap-3">
                <Swatch name="brand" token="--brand" hex="#0A7A3F" />
                <Swatch name="brand-hover" token="--brand-hover" hex="#096834" />
                <Swatch name="chrome" token="--chrome" hex="#0F172A" />
              </div>
            </Card>
            <Card eyebrow="Severity — Attention only">
              <div className="grid grid-cols-2 gap-3">
                <Swatch name="notice-ink" token="--notice-ink" hex="#B45309" />
                <Swatch name="notice-surface" token="--notice-surface" hex="#FBEAD2" />
                <Swatch name="escalate-ink" token="--escalate-ink" hex="#DC2626" />
                <Swatch name="escalate-surface" token="--escalate-surface" hex="#FBE3E3" />
              </div>
            </Card>
            <Card eyebrow="The two data hues">
              <div className="grid grid-cols-2 gap-3">
                <Swatch name="axis-work" token="--axis-work" hex="#3B82F6" />
                <Swatch name="axis-cost" token="--axis-cost" hex="#7E22CE" />
              </div>
              <p className="type-data-label mt-3">
                Hue marks which axis, never how high. Magnitude is position or number.
              </p>
            </Card>
          </div>

          <Card eyebrow="Zone ramps">
            <div className="grid grid-cols-2 gap-6">
              <ZoneRamp axis="work" label="Speed zones — Z1→Z5 (Work)" />
              <ZoneRamp axis="cost" label="HR zones — Z1→Z5 (Cost, detail only)" />
            </div>
          </Card>
        </Section>

        {/* Type roles */}
        <Section
          title="Type roles"
          desc="One header system for every section. Distinct classes, never shared. Numbers use the tabular/mono stack."
        >
          <Card>
            <div className="space-y-6">
              <div>
                <h2 className="type-section-h">Section header</h2>
                <p className="type-section-desc">One-line descriptor sits under every section header.</p>
              </div>
              <div className="space-y-1">
                <div className="type-card-eyebrow">Card eyebrow</div>
                <div className="type-data-label">Data label — 11px, text-secondary</div>
                <div className="type-col-head">Column head</div>
                <div className="type-micro">Micro label</div>
                <div className="type-num text-2xl font-semibold">1,248.65</div>
              </div>
            </div>
          </Card>
        </Section>

        {/* ValueOnTrack */}
        <Section
          title="ValueOnTrack"
          desc="Canonical comparison object. Track band + reference band (typical variation) + reference tick + value in the owning hue + signed % delta. Past the tick = above typical; past the band = beyond normal variation."
        >
          <div className="grid grid-cols-2 gap-4">
            <Card eyebrow="Deviation mode · window ±40%">
              <div className="space-y-4">
                <div className="space-y-1">
                  <div className="type-data-label">Total distance vs athlete reference</div>
                  <ValueOnTrack mode="deviation" axis="work" value={9820} reference={8600} unit="m" deltaAbs="+1,220 m" />
                </div>
                <div className="space-y-1">
                  <div className="type-data-label">Cardio Load vs athlete reference</div>
                  <ValueOnTrack mode="deviation" axis="cost" value={168} reference={195} unit="CL" deltaAbs="−27 CL" />
                </div>
                <div className="space-y-1">
                  <div className="type-data-label">HSR — clamped overflow (+62%)</div>
                  <ValueOnTrack mode="deviation" axis="work" value={890} reference={550} unit="m" deltaAbs="+340 m" />
                </div>
              </div>
            </Card>

            <Card eyebrow="Shared-scale mode · 0–12 km">
              <div className="space-y-3">
                {[
                  { name: "Ortega", v: 10.2, r: 9.4 },
                  { name: "Vidic", v: 7.8, r: 8.9 },
                  { name: "Rossi", v: 11.6, r: 10.1 },
                ].map((row) => (
                  <div key={row.name} className="grid grid-cols-[80px_1fr] items-center gap-3">
                    <div className="type-data-label">{row.name}</div>
                    <ValueOnTrack
                      mode="shared"
                      axis="work"
                      value={row.v}
                      reference={row.r}
                      scaleMin={0}
                      scaleMax={12}
                      unit="km"
                    />
                  </div>
                ))}
              </div>
            </Card>
          </div>

          <Card eyebrow="Reference band — three baseline states">
            <div className="space-y-5">
              <div className="grid grid-cols-[160px_1fr] items-center gap-4">
                <div>
                  <div className="type-data-label" style={{ color: "var(--color-text-primary)" }}>
                    Mature baseline
                  </div>
                  <div className="type-data-label">narrow band — tight normal variation</div>
                </div>
                <ValueOnTrack
                  mode="deviation"
                  axis="work"
                  value={9100}
                  reference={8800}
                  referenceBandPct={0.05}
                  unit="m"
                  baselineState="mature"
                />
              </div>
              <div className="grid grid-cols-[160px_1fr] items-center gap-4">
                <div>
                  <div className="type-data-label" style={{ color: "var(--color-text-primary)" }}>
                    Young baseline
                  </div>
                  <div className="type-data-label">wide band — high uncertainty, still learning</div>
                </div>
                <ValueOnTrack
                  mode="deviation"
                  axis="work"
                  value={9400}
                  reference={8600}
                  referenceBandPct={0.18}
                  unit="m"
                  baselineState="young"
                />
              </div>
              <div className="grid grid-cols-[160px_1fr] items-center gap-4">
                <div>
                  <div className="type-data-label" style={{ color: "var(--color-text-primary)" }}>
                    Building baseline
                  </div>
                  <div className="type-data-label">reference withheld — no false-confident compare</div>
                </div>
                <ValueOnTrack
                  mode="deviation"
                  axis="work"
                  value={7800}
                  reference={8600}
                  unit="m"
                  baselineState="building"
                />
              </div>
            </div>
          </Card>
        </Section>



        {/* GapPair */}
        <Section
          title="GapPair"
          desc="External vs internal on one shared % scale. Filled blue = external, open purple = internal, slate connector = gap."
        >
          <Card eyebrow="% of session peak">
            <div className="space-y-6">
              <GapPair externalPct={82} internalPct={55} />
              <GapPair externalPct={41} internalPct={68} />
            </div>
          </Card>
        </Section>

        {/* TrustMark */}
        <Section
          title="TrustMark"
          desc="One costume at every size. Coverage printed on the value it qualifies."
        >
          <Card>
            <div className="flex items-center gap-10">
              <TrustMark size="sm" value="218" unit="m" coverage={74} />
              <TrustMark size="md" value="9,820" unit="m" coverage={74} />
              <TrustMark size="lg" value="168" unit="CL" coverage={82} />
            </div>
          </Card>
        </Section>

        {/* SeverityGlyphs */}
        <Section
          title="SeverityGlyph"
          desc="Two named tiers, always glyph + word. Exists only inside the Attention card."
        >
          <Card>
            <div className="flex items-center gap-4">
              <SeverityGlyph tier="escalate" />
              <SeverityGlyph tier="notice" />
            </div>
          </Card>
        </Section>

        {/* Selection treatment */}
        <Section
          title="Selection treatment"
          desc="Active pills and segmented controls use slate-800 fill with white text. Never green, never a data hue."
        >
          <Card>
            <div className="flex flex-col gap-6">
              {/* Pills */}
              <div className="flex flex-wrap gap-2">
                {["Squad", "Position", "Line", "Full match"].map((label, i) => (
                  <button
                    key={label}
                    className={`type-micro rounded-full px-3 py-1.5 transition-colors ${
                      i === 0 ? "sel-active" : "sel-idle"
                    }`}
                    style={i !== 0 ? { border: "1px solid var(--color-border)" } : undefined}
                  >
                    {label}
                  </button>
                ))}
              </div>

              {/* Segmented control */}
              <div
                className="inline-flex rounded-md p-1"
                style={{
                  backgroundColor: "var(--color-slate-100)",
                  border: "1px solid var(--color-border)",
                }}
              >
                {["Halves", "15' blocks", "Custom"].map((label, i) => (
                  <button
                    key={label}
                    className={`type-micro rounded px-3 py-1.5 transition-colors ${
                      i === 1 ? "sel-active" : "sel-idle"
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
          </Card>
        </Section>

        {/* Changed-state chip */}
        <Section
          title="Changed-state chip"
          desc="A control holding a non-default value gets slate-100 fill + slate-200 border. Never green."
        >
          <Card>
            <div className="flex items-center gap-3">
              <div className="chip-changed inline-flex items-center gap-2 rounded-md px-2.5 py-1.5">
                <span className="type-data-label">Benchmark</span>
                <span className="type-num text-xs font-semibold" style={{ color: "var(--color-text-primary)" }}>
                  Squad median · Last 6
                </span>
                <button
                  className="type-micro rounded px-1.5 py-0.5 transition-colors hover:bg-white"
                  style={{ color: "var(--color-text-secondary)" }}
                  aria-label="Reset to default"
                >
                  reset ✕
                </button>
              </div>
              <span className="type-data-label">non-default value → recomputes downstream reads</span>
            </div>
          </Card>
        </Section>
      </main>
    </div>
  );
}
