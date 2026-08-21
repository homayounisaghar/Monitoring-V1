import { createFileRoute } from "@tanstack/react-router";
import { ValueOnTrack, TrackAxis } from "@/components/data/ValueOnTrack";
import { GapPair } from "@/components/data/GapPair";
import { TrustMark, WithheldMark } from "@/components/data/TrustMark";
import { SeverityGlyph } from "@/components/data/SeverityGlyph";
import { DegradedBanner } from "@/components/data/DegradedBanner";


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
      {eyebrow ? <div className="type-label mb-3">{eyebrow}</div> : null}
      {children}
    </div>
  );
}

/** Styleguide-only demo bars for the chart-legibility rules. */
function MiniBars({
  values,
  caption,
  labelDetached = false,
  invert = false,
  wrong = false,
}: {
  values: number[];
  caption: string;
  labelDetached?: boolean;
  invert?: boolean;
  wrong?: boolean;
}) {
  const H = 56;
  const max = 150;
  return (
    <div className="space-y-2">
      <div className="flex items-end gap-4" style={{ height: H + 18 }}>
        {values.map((v, i) => {
          const drawn = invert ? max - v + 30 : v;
          const h = Math.max(3, (drawn / max) * H);
          return (
            <div key={i} className="relative flex-1" style={{ height: H + 18 }}>
              <div
                className="absolute bottom-0 left-1/2 w-8 -translate-x-1/2 rounded-[2px]"
                style={{ height: h, backgroundColor: "var(--color-axis-work)" }}
              />
              <span
                className="type-num absolute left-1/2 -translate-x-1/2 text-[11px]"
                style={{
                  bottom: labelDetached ? H + 2 : h + 1,
                  color: "var(--color-text-secondary)",
                }}
              >
                {v}
              </span>
            </div>
          );
        })}
      </div>
      <div
        className="type-label"
        style={{ color: wrong ? "var(--color-escalate-ink)" : "var(--color-text-tertiary)" }}
      >
        {caption}
      </div>
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
              backgroundColor: `var(--zone-${axis}-${n})`,
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

        {/* Type scale — five slots */}
        <Section
          title="Type scale"
          desc="Five slots, ratified. Display is one-per-screen. Micro-caps is for column heads and axis labels only — never a sentence."
        >
          <Card eyebrow="1 · display · one per screen">
            <div className="type-display">1,248.65</div>
            <p className="type-label mt-2">
              Reserved for the single hero read on any given screen. Never used for section headers.
            </p>
          </Card>
          <div className="grid grid-cols-2 gap-4">
            <Card eyebrow="2 · key-value">
              <div className="type-keyvalue">9,820 m</div>
              <div className="type-keyvalue mt-2">168 CL</div>
            </Card>
            <Card eyebrow="3 · data">
              <div className="type-data">Total distance · 9,820 m · +14%</div>
              <div className="type-data">Cardio Load · 168 CL · −14%</div>
              <p className="type-label mt-3">
                Units, ratified. Every numeral carries its unit. In a serialized
                list the unit repeats on every value — never printed once on the
                last item. A delta unit is self-explanatory where it stands.
              </p>
              <div className="mt-2 space-y-1 text-[12.5px]">
                <div className="type-num" style={{ color: "var(--color-text-secondary)" }}>
                  T. Brandt 74% HR cov · S. Kuhn 61% HR cov · F. Voss 43% HR cov
                </div>
                <div
                  className="type-num line-through"
                  style={{ color: "var(--color-escalate-ink)" }}
                >
                  T. Brandt 74 · S. Kuhn 61 · F. Voss 43% HR cov
                </div>
                <div className="type-num" style={{ color: "var(--color-text-secondary)" }}>
                  +22 pts gap
                  <span className="ml-2" style={{ color: "var(--color-text-tertiary)" }}>
                    beside a −14% delta, "+22 pts" alone would not say what it counts
                  </span>
                </div>
              </div>
            </Card>

            <Card eyebrow="4 · label · sentence case, no tracking">
              <p className="type-label">Total distance vs athlete reference</p>
              <p className="type-label">Baseline is still building — 3 of 5 sessions.</p>
            </Card>
            <Card eyebrow="5 · micro-caps · column heads & axis labels only">
              <div className="type-microcaps">Athlete</div>
              <div className="type-microcaps mt-1">Distance (m)</div>
              <div className="type-microcaps mt-1">HSR</div>
            </Card>
          </div>
        </Section>

        {/* Tone ladder */}
        <Section
          title="Tone ladder"
          desc="Canvas → card → inset. Cards are white on a slate canvas with a hairline border and 1dp shadow. Only the Attention card is allowed 2dp. Insets are one step darker than the card, for accounting lines and wells."
        >
          <div className="grid grid-cols-3 gap-4">
            <div className="surface-card rounded-lg p-5">
              <div className="type-microcaps mb-2">Card · 1dp</div>
              <p className="type-label">The default surface for every section card.</p>
              <div className="surface-inset mt-4 rounded-md p-3">
                <div className="type-microcaps mb-1">Inset</div>
                <p className="type-label">One step darker — used for wells inside a card.</p>
              </div>
            </div>
            <div className="surface-card-attention rounded-lg p-5">
              <div className="type-microcaps mb-2">Attention card · 2dp</div>
              <p className="type-label">The only surface allowed the second shadow step.</p>
            </div>
            <div
              className="rounded-lg p-5"
              style={{ backgroundColor: "var(--color-canvas)", border: "1px dashed var(--color-border)" }}
            >
              <div className="type-microcaps mb-2">Canvas</div>
              <p className="type-label">The page background — one step darker than before.</p>
            </div>
          </div>
        </Section>

        {/* Degraded-state banner — ratified pattern */}
        <Section
          title="Degraded-state banner"
          desc="When a whole section or screen cannot be read — insufficient HR coverage, baselines still building — it says so once, in the label slot. The display slot stays reserved for the single hero read; a degraded state is never the hero."
        >
          <Card eyebrow="the pattern">
            <ol className="type-label space-y-1.5" style={{ listStyle: "decimal inside" }}>
              <li>Headline — one line, sentence case, sans. Never the display slot.</li>
              <li>
                Summary — one line stating the extent once. Numerals take the key-value
                slot; the sentence around them stays sans.
              </li>
              <li>
                Detail — collapsed and expandable. Never an enumerated list of every
                affected athlete on arrival, and never sets the banner's height.
              </li>
            </ol>
          </Card>

          <Card eyebrow="live example · no HR data">
            <div className="surface-card-attention overflow-hidden rounded-lg">
              <DegradedBanner
                headline="Can't read the squad today"
                summaryNumeral="18"
                summaryText="of 18 athletes under 80% HR coverage"
                detailCount={3}
              >
                <ul className="px-5 pb-4 pt-3">
                  {["Lange", "Werner", "Köhler"].map((n) => (
                    <li
                      key={n}
                      className="flex items-center gap-3 py-1 text-[13px]"
                      style={{ color: "var(--color-text-secondary)" }}
                    >
                      <span style={{ color: "var(--color-text-primary)" }}>{n}</span>
                      <span className="type-num" style={{ color: "var(--color-text-tertiary)" }}>
                        0% HR cov
                      </span>
                    </li>
                  ))}
                </ul>
              </DegradedBanner>
            </div>
          </Card>

          <Card eyebrow="wrong">
            <div className="type-display" style={{ fontSize: 34 }}>
              Can't read the squad today
            </div>
            <p className="type-label mt-2" style={{ color: "var(--color-escalate-ink)" }}>
              A sentence in the display slot, followed by one row per athlete. Two rules
              broken: display is one-per-screen and numerals only, and the list enumerates
              what the summary already said.
            </p>
          </Card>
        </Section>

        {/* Legacy type roles (compat only) */}

        <Section
          title="Legacy type roles (compat)"
          desc="Kept while sections are re-clothed. New work uses the five slots above."
        >
          <Card>
            <div className="space-y-1">
              <h2 className="type-section-h">Section header</h2>
              <p className="type-section-desc">One-line descriptor sits under every section header.</p>
              <div className="type-label">Card eyebrow</div>
              <div className="type-data-label">Data label — 11px, text-secondary</div>
              <div className="type-col-head">Column head</div>
              <div className="type-micro">Micro label</div>
              <div className="type-num text-2xl font-semibold">1,248.65</div>
            </div>
          </Card>
        </Section>


        {/* ValueOnTrack */}
        <Section
          title="ValueOnTrack"
          desc="Canonical comparison object. Endpoint numerals (mono 10px default / 9px compact, tertiary ink) sit BELOW the track, each centred under its end cap with a 3px gap — the cap is the tick mark and the numeral labels it. They are anatomy of EVERY track, not a header. The hairline spans the full track width, so the drawn range starts exactly where the cap and its numeral sit. Never flank the hairline with inline numerals: that reads as a slider control and implies the range begins after the numeral. Axis-labeling convention (bullet graph): the scale label is centred on its tick, on the opposite side of the axis from the data marks — deltas ride above, the scale reads below. Then: hairline + end caps · reference band (a bounded interval, 16px, slate-200 with slate-300 edges) · 22px reference tick · 8px session dot in the owning axis hue. The signed % delta rides the mark — mono 11px, centred on the dot, 21px above the hairline, in the axis ink. The value column carries the absolute value and its unit, nothing else. One-utterance rule: endpoints are anatomy of every track; the tick label (100 · typical match) is uttered once per scale group per card, by TrackAxis — TrackAxis prints the tick label only, never endpoint numerals. A TrackAxis with no tick label has nothing to say and must not be rendered. Band bounds and the reference absolute live on hover only."
        >
          <div className="grid grid-cols-2 gap-4">
            <Card eyebrow="deviation mode - one tick label above, endpoints under each track">
              <div className="space-y-3">
                <TrackAxis mode="deviation" tickLabel="100 · typical match" />
                <div className="space-y-1">
                  <div className="type-data-label">Total distance vs athlete reference</div>
                  <ValueOnTrack mode="deviation" axis="work" value={9820} reference={8600} unit="m" deltaAbs="+1,220 m" />
                </div>
                <div className="space-y-1">
                  <div className="type-data-label">Cardio Load vs athlete reference</div>
                  <ValueOnTrack mode="deviation" axis="cost" value={168} reference={195} unit="CL" deltaAbs="−27 CL" />
                </div>
                <div className="space-y-1">
                  <div className="type-data-label">HSR — clamped past the window</div>
                  <ValueOnTrack mode="deviation" axis="work" value={890} reference={550} unit="m" deltaAbs="+340 m" />
                </div>
              </div>
            </Card>

            <Card eyebrow="shared absolute mode - unit printed once, under the high end cap">
              <div className="space-y-3">
                <TrackAxis mode="shared" scaleMin={0} scaleMax={12} unit="km" reference={9.5} tickLabel="9.5 · squad typical" leadingGutter={80} />
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

          <Card eyebrow="anatomy - the four marks, and the states">
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
                    Clamped overflow
                  </div>
                  <div className="type-data-label">dot pinned at the end, break glyph inside it, exact % still printed</div>
                </div>
                <ValueOnTrack
                  mode="deviation"
                  axis="cost"
                  value={340}
                  reference={195}
                  unit="CL"
                  deltaAbs="+145 CL"
                />
              </div>
              <div className="grid grid-cols-[160px_1fr] items-center gap-4">
                <div>
                  <div className="type-data-label" style={{ color: "var(--color-text-primary)" }}>
                    Building baseline
                  </div>
                  <div className="type-data-label">no dot, no band, no delta — the hairline states why</div>
                </div>
                <ValueOnTrack
                  mode="deviation"
                  axis="work"
                  value={7800}
                  reference={8600}
                  unit="m"
                  baselineState="building"
                  baselineSessions={3}
                />
              </div>
              <div className="grid grid-cols-[160px_1fr] items-center gap-4">
                <div>
                  <div className="type-data-label" style={{ color: "var(--color-text-primary)" }}>
                    Compact
                  </div>
                  <div className="type-data-label">same anatomy, floors held: dot 6px, delta 10px, band 12px</div>
                </div>
                <ValueOnTrack
                  mode="deviation"
                  axis="work"
                  value={9200}
                  reference={8600}
                  unit="m"
                  size="compact"
                />
              </div>
            </div>
            <p className="type-section-desc mt-4">
              Hover any track: the tooltip carries only the numbers not on canvas — band bounds in
              scale units and the reference absolute with its unit. It never narrates the scale,
              and never repeats the delta or the printed value.
            </p>
          </Card>
        </Section>




        {/* GapPair */}
        <Section
          title="GapPair"
          desc="Work vs cost on one shared track, drawn in the ValueOnTrack anatomy (hairline + end caps, bounded reference band, reference tick). Two canonical dots — work blue, cost purple — under the same tick label as sibling rows; like every track it prints its own endpoint numerals. The distance between the marks is a measurement bracket: 1px slate-500 rail with 4px down-ticks, labelled with the gap in neutral slate (e.g. +27 pts gap). Bracket and label stay neutral — no severity, no third hue. Reads as two marks plus a measured distance, not as a range interval. Hover shows the two component deltas only (e.g. distance +14 · cardio −18), never the printed gap."
        >
          <Card eyebrow="distance vs cardio gap (pts) — pair under the shared axis header, bracket = measured distance">
            <div className="space-y-2">
              <TrackAxis mode="shared" scaleMin={0} scaleMax={100} tickLabel="50 · session average" reference={50} withValueColumn={false} />
              <GapPair externalPct={82} internalPct={55} deltaLabel="+27 pts gap" />
              <GapPair externalPct={41} internalPct={68} deltaLabel="−27 pts gap" />
            </div>
          </Card>
        </Section>

        {/* Chart legibility — ratified rules */}
        <Section
          title="Chart legibility"
          desc="Three ratified rules. They govern every bar, block and track in the system — ValueOnTrack, GapPair, and the Periods blocks matrix."
        >
          <Card eyebrow="a - the value label is attached to its mark">
            <div className="grid grid-cols-2 gap-6">
              <MiniBars
                caption="right"
                labelDetached={false}
                values={[82, 54, 118]}
              />
              <MiniBars
                caption="wrong - label floats in empty row space"
                labelDetached
                values={[82, 54, 118]}
                wrong
              />
            </div>
          </Card>

          <Card eyebrow="b - on a shared scale, drawn size encodes magnitude">
            <div className="grid grid-cols-2 gap-6">
              <MiniBars caption="right - bars grow from a common floor" values={[118, 54, 82]} />
              <MiniBars
                caption="wrong - a smaller value drawn as a larger block"
                values={[118, 54, 82]}
                invert
                wrong
              />
            </div>
            <p className="type-section-desc mt-4">
              Special segments - added time, part-periods - take a narrow, explicitly labelled
              sub-column on the same scale, or a rate annotation. Never a full-height block.
            </p>
          </Card>

          <Card eyebrow="c - row and series names are plain language">
            <div className="type-num flex flex-col gap-1 text-[12.5px]">
              <span style={{ color: "var(--color-text-primary)" }}>
                distance vs cardio gap (pts)
              </span>
              <span style={{ color: "var(--color-text-tertiary)", textDecoration: "line-through" }}>
                gap E-I - pts
              </span>
            </div>
            <p className="type-section-desc mt-3">
              The name is authored once in the copy deck; styleguide, legends and cards inherit it.
            </p>
          </Card>
        </Section>


        {/* TrustMark — trust grammar */}
        <Section
          title="Trust grammar"
          desc="A clean value with a small hollow dot before it. Hover carries the detailed coverage read (e.g. “74% HR coverage”) — but a cell or row whose values are fully withheld states its reason on the canvas. Texture never sits behind numerals anywhere in the system."
        >
          <Card>
            <div className="flex items-center gap-10">
              <TrustMark size="sm" value="218" unit="m" coverage={74} coverageOf="HR coverage" />
              <TrustMark size="md" value="9,820" unit="m" coverage={74} coverageOf="GPS coverage" />
              <TrustMark size="lg" value="168" unit="CL" coverage={82} coverageOf="HR coverage" />
            </div>
            <p className="type-label mt-4">
              Hover any value to see the coverage read. The hollow dot is the trust affordance — the number stays fully legible.
            </p>

            <div
              className="mt-6 border-t pt-4"
              style={{ borderColor: "var(--color-border)" }}
            >
              <div className="type-microcaps mb-2">Withheld states — reason on the canvas</div>
              <p className="type-label mb-3">
                Ratified: a static screenshot must never show an unexplained dash. The
                “building baseline” pattern generalises — every fully withheld cell or row
                prints a short qualifier beside its dash, and hover keeps the longer read.
              </p>
              <div className="flex flex-wrap items-center gap-8">
                <WithheldMark reason="notComparable" detail="26′ — too short to compare" />
                <WithheldMark reason="buildingBaseline" detail="3 of 5 sessions to minimum history" />
                <WithheldMark reason="notSubmitted" />
                <WithheldMark reason="thinCoverage" detail="2 of 6 sessions contributed" />
              </div>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                <div
                  className="rounded-md border p-3"
                  style={{ borderColor: "var(--color-border)" }}
                >
                  <div className="type-microcaps mb-1">Right — row qualifier</div>
                  <div className="type-num text-[13px]">26′ · not comparable</div>
                  <div className="type-num mt-1 text-[13px]" style={{ color: "var(--color-text-tertiary)" }}>
                    —&nbsp;&nbsp;—&nbsp;&nbsp;—
                  </div>
                </div>
                <div
                  className="rounded-md border p-3"
                  style={{ borderColor: "var(--color-border)" }}
                >
                  <div className="type-microcaps mb-1">Wrong — hover-only</div>
                  <div className="type-num text-[13px] line-through" style={{ color: "var(--color-red-700)" }}>
                    26′
                  </div>
                  <div className="type-num mt-1 text-[13px] line-through" style={{ color: "var(--color-red-700)" }}>
                    —&nbsp;&nbsp;—&nbsp;&nbsp;—
                  </div>
                </div>
              </div>
            </div>

            <div
              className="mt-6 border-t pt-4"
              style={{ borderColor: "var(--color-border)" }}
            >
              <div className="type-microcaps mb-2">
                The 80% HR-coverage gate — internal load
              </div>
              <p className="type-label mb-3">
                Ratified: where an athlete&rsquo;s HR coverage for the scope is below 80%
                (0% included), Cardio Load and every other HR-derived value is withheld —
                a dash with its reason, never a number. Squad and window averages are taken
                over the covered athletes only; a withheld athlete is excluded, never counted
                at zero. A value must never appear on a screen that also states the metric
                was not measured. Between the gate and full coverage the value prints with
                its hollow trust dot and its coverage read.
              </p>
              <div className="grid gap-3 md:grid-cols-2">
                <div
                  className="rounded-md border p-3"
                  style={{ borderColor: "var(--color-border)" }}
                >
                  <div className="type-microcaps mb-1">Right — 61% coverage</div>
                  <div className="flex items-center justify-between">
                    <span className="type-label">S. Kuhn · Cardio Load</span>
                    <WithheldMark
                      reason="noHrCoverage"
                      detail="61% HR coverage — below the 80% gate, internal load withheld"
                    />
                  </div>
                  <div className="mt-2 flex items-center justify-between">
                    <span className="type-label">Squad avg · covered only</span>
                    <TrustMark size="sm" value="196" unit="CL" coverage={86} coverageOf="HR coverage" />
                  </div>
                </div>
                <div
                  className="rounded-md border p-3"
                  style={{ borderColor: "var(--color-border)" }}
                >
                  <div className="type-microcaps mb-1">Wrong — value under the gate</div>
                  <div className="flex items-center justify-between">
                    <span className="type-label">S. Kuhn · Cardio Load</span>
                    <span
                      className="type-num text-[13px] line-through"
                      style={{ color: "var(--color-red-700)" }}
                    >
                      142 CL
                    </span>
                  </div>
                  <div className="mt-2 flex items-center justify-between">
                    <span className="type-label">Squad avg · zeros counted</span>
                    <span
                      className="type-num text-[13px] line-through"
                      style={{ color: "var(--color-red-700)" }}
                    >
                      118 CL
                    </span>
                  </div>
                </div>
              </div>
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
