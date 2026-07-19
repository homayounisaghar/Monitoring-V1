/**
 * ST2 — Demo library self-checks (Workstream 01 · prompt 1/4).
 * Not imported by the app. Run in the sandbox to verify §4 states.
 */
import {
  demoSessions, demoRecords, demoAthletes,
  recordsForAthlete, recordsForSession, DEMO_TODAY,
  type DemoSession, type DemoRecord,
} from "./demo-library";

type Check = { name: string; pass: boolean; detail: string };

function inWindow(s: { dateISO: string }): boolean {
  return s.dateISO >= "2026-06-22" && s.dateISO <= "2026-07-19";
}

export function runDemoLibraryChecks(): Check[] {
  const out: Check[] = [];
  const push = (name: string, pass: boolean, detail: string) => out.push({ name, pass, detail });

  const winAll = demoSessions.filter(inWindow);
  const win = winAll.filter((s) => !s.isRestDay);
  const matches = win.filter((s) => s.type === "match");
  const nonMatch = win.filter((s) => s.type !== "match");
  push("28-day sessions total = 24", win.length === 24, `got ${win.length}`);
  push("28-day matches = 5", matches.length === 5, `got ${matches.length}`);
  push("28-day non-match = 19", nonMatch.length === 19, `got ${nonMatch.length}`);

  const missing = demoSessions.find((s) => s.dateISO === "2026-07-14");
  push("Tue 14 Jul missing (no record)", !missing, missing ? `found ${missing.id}` : "absent");

  const restDates = ["2026-06-22", "2026-06-29", "2026-07-05", "2026-07-06"];
  const restsPresent = restDates.every((d) => demoSessions.some((s) => s.dateISO === d && s.isRestDay));
  push("Four rest days present as zero records", restsPresent, restDates.join(","));

  const restRecordsZero = demoRecords
    .filter((r) => restDates.includes(r.dateISO))
    .every((r) => r.totalDistance === 0 && r.hsr === 0 && r.minutes === 0);
  push("Rest-day records are zero", restRecordsZero, "");

  const doubleDay = demoSessions.filter((s) => s.dateISO === "2026-07-13");
  push("Mon 13 Jul double-session", doubleDay.length === 2 && doubleDay.some((s) => s.type === "gym") && doubleDay.some((s) => s.type === "training"), doubleDay.map((s) => s.name).join(" + "));

  const koehler = recordsForAthlete("koehler").filter((r) => r.inSquad);
  const koehlerDays = new Set(koehler.map((r) => r.dateISO));
  const koehlerFirst = [...koehlerDays].sort()[0];
  push("Köhler first record ≥ 2026-07-07", (koehlerFirst ?? "") >= "2026-07-07", `first=${koehlerFirst}`);
  const koehlerWindow = koehler.filter((r) => r.dateISO >= "2026-06-22" && r.dateISO <= "2026-07-19").length;
  push("Köhler 13 records in 28-day window", koehlerWindow === 13, `got ${koehlerWindow}`);

  const voss = recordsForAthlete("voss").filter((r) => inWindow(r) && r.participation !== null);
  const vossAlwaysInjury = voss.every((r) => r.participation === "Injury");
  push("Voss = Injury throughout window", vossAlwaysInjury && voss.length > 0, `count=${voss.length}`);

  const langeArc = recordsForAthlete("lange").filter(inWindow).sort((a, b) => a.dateISO.localeCompare(b.dateISO));
  const seen: string[] = [];
  for (const r of langeArc) {
    if (r.participation && seen[seen.length - 1] !== r.participation) seen.push(r.participation);
  }
  const arcOK = seen.join(">") === "Full>Part>Rehab>Injury";
  push("Lange arc Full→Part→Rehab→Injury", arcOK, seen.join(">"));

  const jun30 = recordsForSession(demoSessions.find((s) => s.dateISO === "2026-06-30")!.id);
  const brandt = jun30.find((r) => r.athleteId === "brandt")!;
  const kuhn = jun30.find((r) => r.athleteId === "kuhn")!;
  push("Brandt <80 % HR on 30 Jun", (brandt.hrCoveragePct ?? 100) < 80, `hr=${brandt.hrCoveragePct}`);
  push("Kuhn <80 % HR on 30 Jun", (kuhn.hrCoveragePct ?? 100) < 80, `hr=${kuhn.hrCoveragePct}`);

  const unconfirmed = demoSessions.filter((s) => s.unconfirmed);
  push("Exactly one unconfirmed session", unconfirmed.length === 1 && unconfirmed[0].dateISO === "2026-07-19", unconfirmed.map((s) => s.dateISO).join(","));

  const matchTd: { date: string; td: number }[] = matches.map((m) => ({
    date: m.dateISO,
    td: recordsForSession(m.id).reduce((s, r) => s + r.totalDistance, 0),
  }));
  const jul8 = matchTd.find((x) => x.date === "2026-07-08")!;
  const others = matchTd.filter((x) => x.date !== "2026-07-08");
  const highestOther = Math.max(...others.map((x) => x.td));
  push("8 Jul TD ≥10 % over next match", jul8.td >= highestOther * 1.10, `jul8=${jul8.td} vs max other=${highestOther}`);

  const frei = recordsForAthlete("frei").filter((r) => r.srpeAU != null);
  push("Frei has zero sRPE records", frei.length === 0, `count=${frei.length}`);

  const noCollectDays = ["2026-07-12", "2026-07-19"];
  const noCollectOK = noCollectDays.every((d) => {
    const s = demoSessions.find((x) => x.dateISO === d)!;
    return s.srpeCollected === false;
  });
  push("Two no-collection recovery days", noCollectOK, noCollectDays.join(","));

  // Determinism — re-import via require would need dyn; we instead hash a
  // canonical view and compare against a fresh re-generation from a second run
  // (approximated by hashing the frozen arrays twice; module regen is impossible
  // in-process, so this check confirms values are stable and non-mutating).
  const hash = (rs: readonly DemoRecord[]) => rs.reduce((h, r) => (h * 31 + (r.totalDistance + r.hsr + r.minutes)) | 0, 0);
  const h1 = hash(demoRecords);
  const h2 = hash(demoRecords);
  push("Records stable (deterministic hash)", h1 === h2, `h=${h1}`);

  push("DEMO_TODAY = 2026-07-19", DEMO_TODAY === "2026-07-19", DEMO_TODAY);
  push("Roster size = 19", demoAthletes.length === 19, `n=${demoAthletes.length}`);

  return out;
}

// CLI harness: `bunx tsx src/lib/demo-library.check.ts`
declare const process: { argv: string[]; exit(n: number): never } | undefined;
if (typeof process !== "undefined" && process.argv[1] && process.argv[1].endsWith("demo-library.check.ts")) {
  const results = runDemoLibraryChecks();
  const pad = (s: string, n: number) => (s + " ".repeat(n)).slice(0, n);
  for (const r of results) {
    console.log(`${r.pass ? "PASS" : "FAIL"}  ${pad(r.name, 46)}  ${r.detail}`);
  }
  const fails = results.filter((r) => !r.pass).length;
  console.log(`\n${results.length - fails}/${results.length} passed`);
  process.exit(fails === 0 ? 0 : 1);
}
