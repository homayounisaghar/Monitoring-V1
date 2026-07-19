/**
 * ST2 — Demo library self-checks (Workstream 01 · prompt 1/4, corrections 1b).
 * Not imported by the app. Run in the sandbox to verify §-level invariants.
 */
import {
  demoSessions, demoRecords, demoAthletes, demoDays,
  recordsForAthlete, recordsForSession, DEMO_TODAY,
  buildSessions, buildDays, buildRecords,
  DAY_TD_DOMAIN_MAX,
  type DemoRecord,
} from "./demo-library";

type Check = { name: string; pass: boolean; detail: string };

function inWindow(s: { dateISO: string }): boolean {
  return s.dateISO >= "2026-06-22" && s.dateISO <= "2026-07-19";
}

export function runDemoLibraryChecks(): Check[] {
  const out: Check[] = [];
  const push = (name: string, pass: boolean, detail: string) => out.push({ name, pass, detail });

  const win = demoSessions.filter(inWindow);
  const matches = win.filter((s) => s.type === "match");
  const nonMatch = win.filter((s) => s.type !== "match");
  push("28-day sessions total = 24", win.length === 24, `got ${win.length}`);
  push("28-day matches = 5", matches.length === 5, `got ${matches.length}`);
  push("28-day non-match = 19", nonMatch.length === 19, `got ${nonMatch.length}`);

  // demoDays checks (§2).
  const day714 = demoDays.find((d) => d.dateISO === "2026-07-14");
  push("demoDays has no entry for 14 Jul", !day714, day714 ? "present" : "absent");
  const restDates = ["2026-06-22", "2026-06-29", "2026-07-05", "2026-07-06"];
  const restsAsDays = restDates.every((d) => demoDays.find((x) => x.dateISO === d)?.kind === "rest");
  push("Four rest dates present as demoDays kind=rest", restsAsDays, restDates.join(","));

  const missingSession = demoSessions.find((s) => s.dateISO === "2026-07-14");
  push("Tue 14 Jul missing (no session)", !missingSession, missingSession ? `found ${missingSession.id}` : "absent");

  const restRecordsZero = demoRecords
    .filter((r) => restDates.includes(r.dateISO))
    .every((r) => r.totalDistance === 0 && r.hsr === 0 && r.minutes === 0 && r.sessionId === null);
  push("Rest-day records zero and sessionId null", restRecordsZero, "");

  const doubleDay = demoSessions.filter((s) => s.dateISO === "2026-07-13");
  push("Mon 13 Jul double-session",
    doubleDay.length === 2 && doubleDay.some((s) => s.type === "gym") && doubleDay.some((s) => s.type === "training"),
    doubleDay.map((s) => s.name).join(" + "));

  // §1 — every non-match session's name day-code must equal dayCodeFor(dateISO).
  const codeRe = /^(MD[-+]\d)/;
  const badCode = demoSessions
    .filter((s) => s.type !== "match")
    .map((s) => {
      const m = s.name.match(codeRe);
      if (!m) return null;
      return m[1] === s.dayCode ? null : `${s.dateISO}: name=${m[1]} dayCode=${s.dayCode}`;
    })
    .filter((x): x is string => x !== null);
  push("Non-match session name day-code matches dayCode (§1)", badCode.length === 0, badCode.join(" | "));

  const koehler = recordsForAthlete("koehler").filter((r) => r.inSquad);
  const koehlerDays = new Set(koehler.map((r) => r.dateISO));
  const koehlerFirst = [...koehlerDays].sort()[0];
  push("Köhler first record ≥ 2026-07-07", (koehlerFirst ?? "") >= "2026-07-07", `first=${koehlerFirst}`);
  const koehlerWindow = koehler.filter(inWindow).length;
  push("Köhler 13 records in 28-day window", koehlerWindow === 13, `got ${koehlerWindow}`);

  const voss = recordsForAthlete("voss").filter((r) => inWindow(r) && r.participation !== null);
  const vossAlwaysInjury = voss.every((r) => r.participation === "Injury");
  push("Voss = Injury throughout window", vossAlwaysInjury && voss.length > 0, `count=${voss.length}`);
  const vossZeroMinutes = recordsForAthlete("voss")
    .filter((r) => inWindow(r) && r.sessionId !== null && r.sessionId !== "s-2026-07-04-dortmund")
    .every((r) => r.minutes === 0);
  push("Voss zero minutes on all pre-pinned window sessions (§3)", vossZeroMinutes, "");

  const langeArc = recordsForAthlete("lange").filter((r) => inWindow(r) && r.sessionId !== null)
    .sort((a, b) => a.dateISO.localeCompare(b.dateISO));
  const seen: string[] = [];
  for (const r of langeArc) {
    if (r.participation && seen[seen.length - 1] !== r.participation) seen.push(r.participation);
  }
  push("Lange arc Full→Part→Rehab→Injury", seen.join(">") === "Full>Part>Rehab>Injury", seen.join(">"));

  const jun30Session = demoSessions.find((s) => s.dateISO === "2026-06-30");
  const jun30 = jun30Session ? recordsForSession(jun30Session.id) : [];
  const brandt = jun30.find((r) => r.athleteId === "brandt");
  const kuhn = jun30.find((r) => r.athleteId === "kuhn");
  push("Brandt <80 % HR on 30 Jun", !!brandt && (brandt.hrCoveragePct ?? 100) < 80, `hr=${brandt?.hrCoveragePct}`);
  push("Kuhn <80 % HR on 30 Jun", !!kuhn && (kuhn.hrCoveragePct ?? 100) < 80, `hr=${kuhn?.hrCoveragePct}`);

  const unconfirmed = demoSessions.filter((s) => s.unconfirmed);
  push("Exactly one unconfirmed session", unconfirmed.length === 1 && unconfirmed[0].dateISO === "2026-07-19", unconfirmed.map((s) => s.dateISO).join(","));

  // Beyond-range: verified against a fixed drawn domain, not a %-vs-peer trick.
  // (a) Exactly one calendar day in the full library exceeds DAY_TD_DOMAIN_MAX,
  // and that day is 2026-07-08. (b) No athlete-session exceeds 15,000 m — the
  // plausibility floor the retired multiplier was breaching.
  const dayTotals = new Map<string, number>();
  for (const r of demoRecords) {
    dayTotals.set(r.dateISO, (dayTotals.get(r.dateISO) ?? 0) + r.totalDistance);
  }
  const overCap = [...dayTotals.entries()].filter(([, td]) => td > DAY_TD_DOMAIN_MAX);
  push(
    `Exactly one day exceeds DAY_TD_DOMAIN_MAX=${DAY_TD_DOMAIN_MAX} and it is 8 Jul`,
    overCap.length === 1 && overCap[0][0] === "2026-07-08",
    overCap.map(([d, td]) => `${d}=${td}`).join(", ") || "none",
  );
  const maxAthleteTd = demoRecords.reduce((m, r) => Math.max(m, r.totalDistance), 0);
  const maxRec = demoRecords.find((r) => r.totalDistance === maxAthleteTd);
  push(
    "No athlete-session exceeds 15,000 m total distance",
    maxAthleteTd <= 15000,
    `max=${maxAthleteTd} m (${maxRec?.athleteId} on ${maxRec?.dateISO})`,
  );

  const frei = recordsForAthlete("frei").filter((r) => r.srpeAU != null);
  push("Frei has zero sRPE records", frei.length === 0, `count=${frei.length}`);

  const noCollectDays = ["2026-07-12", "2026-07-19"];
  const noCollectOK = noCollectDays.every((d) => {
    const s = demoSessions.find((x) => x.dateISO === d);
    return s?.srpeCollected === false;
  });
  push("Two no-collection recovery days", noCollectOK, noCollectDays.join(","));

  // §4 — match squad shape: exactly 11 rows with minutes ≥ 85; 3–5 Part rows.
  // Pinned Dortmund exempt.
  const shapeIssues: string[] = [];
  const starterCounts = new Map<string, number>();
  const nonPinnedMatches = matches.filter((m) => m.id !== "s-2026-07-04-dortmund");
  for (const m of nonPinnedMatches) {
    const rs = recordsForSession(m.id);
    const starters = rs.filter((r) => r.participation === "Full" && r.minutes >= 85);
    const parts = rs.filter((r) => r.participation === "Part");
    if (starters.length !== 11) shapeIssues.push(`${m.dateISO} starters=${starters.length}`);
    if (parts.length < 3 || parts.length > 5) shapeIssues.push(`${m.dateISO} parts=${parts.length}`);
    for (const r of starters) starterCounts.set(r.athleteId, (starterCounts.get(r.athleteId) ?? 0) + 1);
  }
  push("Each non-pinned match: 11 starters ≥85′ and 3–5 Part (§4)", shapeIssues.length === 0, shapeIssues.join(" | "));

  // Keller is the roster's only GK, so he is always the starting keeper — exempt.
  const alwaysStarter = Array.from(starterCounts.entries())
    .filter(([id, c]) => id !== "keller" && c === nonPinnedMatches.length);
  push("No outfield athlete is starter in every match (§4)", alwaysStarter.length === 0, alwaysStarter.map(([id]) => id).join(","));

  // §4 — all six participation tags occur at least once in the 28-day window.
  const tagsSeen = new Set<string>();
  for (const r of demoRecords) if (inWindow(r) && r.participation) tagsSeen.add(r.participation);
  const wantedTags = ["Full", "Part", "Modified", "Other", "Rehab", "Injury"];
  const missingTags = wantedTags.filter((t) => !tagsSeen.has(t));
  push("All six participation tags occur in window (§4)", missingTags.length === 0, missingTags.length ? `missing: ${missingTags.join(",")}` : Array.from(tagsSeen).sort().join(","));

  // §5 — real determinism: re-run builders and deep-compare.
  const s2 = buildSessions();
  const d2 = buildDays();
  const r2 = buildRecords();
  const firstDiff = <T,>(a: readonly T[], b: readonly T[], label: string): string | null => {
    if (a.length !== b.length) return `${label}: length ${a.length} vs ${b.length}`;
    for (let i = 0; i < a.length; i++) {
      const A = JSON.stringify(a[i]);
      const B = JSON.stringify(b[i]);
      if (A !== B) return `${label}[${i}]: ${A} !== ${B}`;
    }
    return null;
  };
  const detSess = firstDiff(demoSessions, s2, "sessions");
  const detDays = firstDiff(demoDays, d2, "days");
  const detRecs = firstDiff(demoRecords, r2, "records");
  const detFail = [detSess, detDays, detRecs].filter(Boolean).join(" | ");
  push("Builders deterministic (deep-equal on re-run) (§5)", detFail === "", detFail);

  push("DEMO_TODAY = 2026-07-19", DEMO_TODAY === "2026-07-19", DEMO_TODAY);
  push("Roster size = 19", demoAthletes.length === 19, `n=${demoAthletes.length}`);

  return out;
}

declare const process: { argv: string[]; exit(n: number): never } | undefined;
if (typeof process !== "undefined" && process.argv[1] && process.argv[1].endsWith("demo-library.check.ts")) {
  const results = runDemoLibraryChecks();
  const pad = (s: string, n: number) => (s + " ".repeat(n)).slice(0, n);
  for (const r of results) {
    console.log(`${r.pass ? "PASS" : "FAIL"}  ${pad(r.name, 62)}  ${r.detail}`);
  }
  const fails = results.filter((r) => !r.pass).length;
  console.log(`\n${results.length - fails}/${results.length} passed`);
  process.exit(fails === 0 ? 0 : 1);
}
// Silence unused-import warning if types get tree-shaken.
export type _DemoRecord = DemoRecord;
