import { createFileRoute } from "@tanstack/react-router";
import { ValueOnTrack } from "@/components/data/ValueOnTrack";
import { GapPair } from "@/components/data/GapPair";
import { TrustMark } from "@/components/data/TrustMark";
import { SeverityGlyph } from "@/components/data/SeverityGlyph";

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
          <Card eyebrow="basis - stated per surface (demo: % of session-average rate)">
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
                {["Halves", "15' blocks"].map((label, i) => (
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
                  last match
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
